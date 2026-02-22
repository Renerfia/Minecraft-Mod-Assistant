import os
from dotenv import load_dotenv
import pandas as pd
from smolagents import LiteLLMModel, ToolCallingAgent, tool, CodeAgent
import requests

load_dotenv()

# Ensure mods folder exists for server deployment
os.makedirs('./mods', exist_ok=True)

API_KEY = os.getenv("MISTRAL_API_KEY")
model = LiteLLMModel(model_id="mistral/mistral-large-2512", api_key=API_KEY)

instructions = """
You are a Minecraft mod assistant. Follow these instructions:

1. Answer questions about mods using the mod_info_fn tool. Always mention the title, description, downloads, version, category, and link.
2. If the user asks to download a mod, use the download_mod_fn tool. Ask the user for the Minecraft version and mod loader if they haven't provided it.
3. Write in plain conversational text. Do not use **, ##, ---, or any markdown formatting.
4. You can use emojis to express yourself naturally.
5.most user might be new to modding so explain things in a simple and easy to understand way.
6. if you want present about mod's data by ordering them in a list or table use bullet points or numbered list.
7. also tell them dependencies if the mod has any.
"""


    
@tool
def mod_info_fn(mod_full_name:str)->str:
    """
    Docstring for mod_info_fn
    
    Args:
    mod_full_name: The full name of the Minecraft mod you want information about.
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
        game_version: The target Minecraft version (e.g., '1.21.1').
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

    



agent = ToolCallingAgent(model=model, tools=[ mod_info_fn, download_mod_fn], instructions=instructions)

history = [] #store the history of interactions with the agent, if needed for context in future interactions
def ask_agent(question,history=history):
    response = agent.run(f"history: {history}\n question: {question}")
    return str(response)   

if __name__ == "__main__":
    question = "can you tell me more about fabric api?"
    response = ask_agent(question)
    print("Agent Response:\n", response)