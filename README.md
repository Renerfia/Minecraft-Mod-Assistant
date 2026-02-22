<div align="center">
  
# 🎮 Minecraft Mod Assistant

*Your personal AI-powered companion for discovering, researching, and downloading Minecraft mods directly to your desktop!*

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![UI Framework](https://img.shields.io/badge/UI-CustomTkinter-brightgreen?style=for-the-badge)](https://github.com/TomSchimansky/CustomTkinter)
[![AI Powered](https://img.shields.io/badge/AI-Mistral_Large-orange?style=for-the-badge&logo=probot)](https://mistral.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

</div>

---

## ✨ Overview

**Minecraft Mod Assistant** is a native Windows desktop application built to streamline your Minecraft modding experience. Instead of endlessly scrolling through forums or websites, simply ask the AI! 

Powered by **Mistral AI** and packaged in a beautiful, modern UI using **CustomTkinter**, this app allows you to research mods, get recommendations, and even automatically download them directly to your computer with a single command.

<p align="center">
  <img src="./images/Capture.png" alt="UI Inspiration" width="400" style="border-radius: 10px;"/>
</p>

---

## 🚀 Key Features

- **🤖 AI Agent Integration:** Ask questions naturally. Example: *"What does the Sodium mod do?"*
- **📦 Direct Downloading:** Say *"Download sodium for fabric 1.21.1"* and the app fetches and saves the `.jar` file directly to your local `mods/` folder!
- **🎨 Modern Dark/Light Mode UI:** The app automatically matches your Windows system theme for a seamless, sleek look.
- **⚡ Multithreaded Performance:** The UI remains snappy and responsive even while the AI is "thinking" or downloading large files.
- **🏃‍♂️ Standalone Package:** Can be compiled into a single `.exe` file so your friends can use it without needing to install Python.

---

## 🛠️ Installation & Setup

If you want to run the app from the source code, follow these steps:

### 1. Prerequisites
Ensure you have Python 3.10 or higher installed.

### 2. Clone & Install Dependencies
Open your terminal in the project directory and run:
```bash
pip install -r requirements.txt
```

### 3. Environment Variables
You need an API key for the AI to function. Create a `.env` file in the root directory and add your Mistral API key:
```env
MISTRAL_API_KEY=your_api_key_here (get api key from: https://docs.mistral.ai)
```

### 4. Run the App
```bash
python app.py
```


## 💡 How to Use

1. **Launch** the ModAssistantApp.
2. **Type your query** in the bottom text box. 
   - *Example: "Give me the link to Wizards of Lua"*
   - *Example: "Download Iris for fabric 1.20"*
3. **Wait** for the Assistant to respond.
4. If you requested a download, click the shiny green **📁 Open Download Folder** button to instantly see your new `.jar` file!

---

## 🏗️ Technologies Used

* **[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)** - For the gorgeous, responsive desktop UI.
* **[smolagents](https://github.com/huggingface/smolagents)** - To power the Tool Calling Agent architecture.
* **[LiteLLM](https://github.com/BerriAI/litellm)** - For seamless integration with the Mistral API.
* **[PyInstaller](https://pyinstaller.org/en/stable/)** - To bundle the Python script into a native Windows executable.

<div align="center">
  <br>
  <i>Built with ❤️ for the Minecraft community.</i>
</div>
