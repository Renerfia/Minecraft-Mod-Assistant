import os
from dotenv import load_dotenv
import pandas as pd
from smolagents import LiteLLMModel, ToolCallingAgent, tool, CodeAgent, WebSearchTool
import requests
import litellm
import json

litellm._turn_on_debug()
load_dotenv()

# Ensure mods folder exists for server deployment
os.makedirs('./mods', exist_ok=True)

API_KEY = os.getenv("MISTRAL_API_KEY")
model = LiteLLMModel(model_id="mistral/mistral-large-2512", api_key=API_KEY) #mistral/mistral-large-2512

instructions = """
You are a Minecraft mod assistant.

- Use mod_info_fn to get mod details. If not found, use web search with short keywords only (e.g. "fabric api modrinth").
- Use download_mod_fn to download mods. Ask for version and loader if not provided.
- ALWAYS use the exact version the user specifies. Never question or substitute it. The API handles validation.
- If user asks for the latest version, use mod_info_fn first to find the latest supported version, then download it.
- Reply in plain conversational text. No markdown, no **, no ##.
- Use emojis naturally. Keep explanations simple for beginners.
- Always mention dependencies if a mod has any.
- Call tools one by one, not in parallel.
- Reply in plain text only. No asterisks, no bold, no headers, no markdown of any kind. If you use ** or ## you are breaking the rules.
- CRITICAL: You must call only ONE tool per step. Wait for the result before calling the next tool. Never include more than one tool call in a single response.
"""
conversation_history = "./conversation_history.json"
def save_history(history):
    with open(conversation_history, "w") as f:
        json.dump(history, f, indent=4)

def load_history():
    if os.path.exists(conversation_history):
        with open(conversation_history, "r") as f:
            return json.load(f)
    return []

    
@tool
def mod_info_fn(mod_full_name:str)->str:
    """
    Docstring for mod_info_fn use this if user wanted to know about a mod's details like description, downloads, version, category, and link. You can also include dependencies if the mod has any.
    
    Args:
    mod_full_name:only minecraft's mod name like wizards-of-lua(user will give simple name like wizards of lua. you just have to replace '-' instead of space.  ) or HW3198Ve. Do not include the version or mod loader in the name, just the mod's name itself.
    """
    params = {
        "query": mod_full_name,
        "limit": 5
    }
    response = requests.get(f"https://api.modrinth.com/v2/search",params=params)
    return response.json()
@tool
def download_mod_fn(mod_id_or_slug: str, game_version: str, loader: str) -> str:
    """
    Downloads a Minecraft mod from Modrinth using its ID or slug, game version, and loader.
    Files are automatically saved to ./mods/ folder for server serving.
    
    Args:
        mod_id_or_slug: The Modrinth project ID or slug (e.g., 'HW3198Ve' or 'wizards-of-lua').
        game_version: The target Minecraft version (e.g., '1.21.11').
        loader: The target Mod loader (e.g., 'fabric', 'forge').
    """
    save_directory = './mods'
    url = f"https://api.modrinth.com/v2/project/{mod_id_or_slug}/version"
    
    # Query parameters required by Modrinth for version filtering
    params = {
        "game_versions": f'["{game_version}"]',
        "loaders": f'["{loader}"]'
    }
    
    # Modrinth API requires a user-agent header
    headers = {"User-Agent": "mod_agent/1.0"}
    
    response = requests.get(url, params=params, headers=headers)
    if response.status_code != 200:
        return f"Failed to fetch versions for mod {mod_id_or_slug}. API Status: {response.status_code}"
    
    versions = response.json()
    print(f"versions: {versions}")
    if not versions:
        return f"No suitable version found for mod {mod_id_or_slug} on {loader} {game_version}."
        
    latest_version = versions[0]
    
    target_file = None
    for file in latest_version.get("files", []):
        if file.get("primary"):
            target_file = file
            break
            
    if not target_file and latest_version.get("files"):
         target_file = latest_version["files"][0]
         
    if not target_file:
         return f"No downloadable files found for this version of {mod_id_or_slug}."
         
    download_url = target_file["url"]
    filename = target_file["filename"]
    
    os.makedirs(save_directory, exist_ok=True)
    file_path = os.path.join(save_directory, filename)
    
    download_response = requests.get(download_url, headers=headers)
    if download_response.status_code != 200:
        return f"Failed to download the mod file. Status: {download_response.status_code}"
        
    with open(file_path, "wb") as f:
        f.write(download_response.content)
        
    return f"Successfully downloaded {filename} to {file_path}."

    



agent = CodeAgent(
    model=model,
    tools=[ mod_info_fn, download_mod_fn, WebSearchTool()],
    instructions=instructions,
    #max_tool_threads=1 # Force sequential tool calls to maintain context
    additional_authorized_imports=["requests", "json", "os", "time","pandas"]
)

#store the history of interactions with the agent, if needed for context in future interactions
def ask_agent(question,history=None):
    history = load_history() if history is None else history
    response = agent.run(f"history: {history[-5:]}\n user question: {question}")
    history.append({"user question": question, "Agent response": str(response)})
    save_history(history)
    return str(response)   

if __name__ == "__main__":
    question = "can you tell me more about fabric api?"
    response = ask_agent(question)
    print("Agent Response:\n", response)