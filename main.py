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

instructions = """You are a minecraft mod analysis assistant. you will answer the questions based on the following dataset and online research.
also prioritize the key title,description, downloads, version, category, and link when answering questions about the mods. if you need to do online research, use the mod_info_fn tool to get information about a specific mod.
if the user asks you to download a mod, use the download_mod_fn tool with the mod's id or slug, game version, and loader. Downloads are automatically saved to the ./mods/ folder on the server. Always provide the user with the downloaded file path. Make sure to ask the user for the necessary information if they haven't provided it."""


    
@tool
def mod_info_fn(mod_full_name:str)->str:
    """
    Docstring for mod_info_fn
    
    Args:
    mod_full_name: The full name of the Minecraft mod you want information about.
    """
    df = pd.read_json("content.json",encoding="utf-8")
    df = pd.DataFrame(df["hits"].tolist())  # adjust based on actual JSON structure
    mod_info = df[df["title"].str.lower() == mod_full_name.lower()]
    return mod_info.to_string() if not mod_info.empty else f"No information found for mod: {mod_full_name}"

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

    



agent = CodeAgent(model=model, tools=[ mod_info_fn, download_mod_fn], instructions=instructions,additional_authorized_imports=["pandas","json",])

history = [] #store the history of interactions with the agent, if needed for context in future interactions
def ask_agent(question,history=history):
    response = agent.run(f"history: {history}\n question: {question}")
    return str(response)   

if __name__ == "__main__":
    question = "can you give me the link of wizards of lua?"
    response = ask_agent(question)
    print("Agent Response:\n", response)