import customtkinter as ctk
import threading
import re
import os
import main

# Set the theme and color for the modern desktop application
ctk.set_appearance_mode("System")  # Uses the user's OS dark/light mode
ctk.set_default_color_theme("blue")  # Sets the color of buttons and widgets

class MinecraftModApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Window Configuration ---
        self.title("Minecraft Mod Assistant")
        self.geometry("850x650")
        self.minsize(600, 450)
        
        # Maintain chat history just like the web version
        self.chat_history = []
        
        # --- UI Layout Design ---
        # Configure a 1-column layout where the chat display takes most of the vertical space
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1) # Chat display row expands
        
        # 1. Chat Display Area (Scrollable to fit all messages)
        self.chat_display = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.chat_display.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="nsew")
        self.chat_display.grid_columnconfigure(0, weight=1)
        
        # 2. Input Area (Frame to hold text box and send button)
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1) # The text box will expand
        
        # 3. Input Textbox
        self.msg_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Ask about mods or say: download sodium for fabric 1.21.1",
            height=45,
            font=("Arial", 14)
        )
        self.msg_entry.grid(row=0, column=0, padx=(0, 15), sticky="ew")
        # Bind the Enter key so users don't have to click the button every time
        self.msg_entry.bind("<Return>", lambda event: self.send_message())
        
        # 4. Send Button
        self.send_button = ctk.CTkButton(
            self.input_frame, 
            text="Send", 
            font=("Arial", 14, "bold"),
            width=100, 
            height=45,
            command=self.send_message
        )
        self.send_button.grid(row=0, column=1, sticky="e")
        
        # 5. Open Downloads Button
        self.downloads_button = ctk.CTkButton(
            self.input_frame, 
            text="📁 Downloads", 
            font=("Arial", 14, "bold"),
            width=120, 
            height=45,
            fg_color="#2ba745", hover_color="#2ea043", # Green color for distinguishing it
            command=self.open_downloads_folder
        )
        self.downloads_button.grid(row=0, column=2, padx=(10, 0), sticky="e")
        
        # Initial greeting from Assistant
        self.add_message("Assistant", "Hello! I am the Minecraft Mod Assistant!\nAsk me about mods or ask me to download them.", is_user=False)
        
    def add_message(self, sender_name, text, is_user=False, filepath=None):
        """
        Creates and adds a text bubble to the scrollable chat display.
        If a filepath is provided, it also creates an 'Open Folder' button.
        """
        # Outer frame for alignment
        msg_frame = ctk.CTkFrame(self.chat_display, fg_color="transparent")
        msg_frame.grid(column=0, sticky="e" if is_user else "w", pady=8, padx=10)
        
        # Bubble styling based on who is sending the message
        bubble_color = ("#0064d2", "#0064d2") if is_user else ("#e5e5ea", "#2b2b2b")
        text_color = ("white", "white") if is_user else ("black", "white")
        
        # Inner bubble frame
        bubble = ctk.CTkFrame(msg_frame, fg_color=bubble_color, corner_radius=15)
        bubble.grid(row=0, column=0, sticky="e" if is_user else "w")
        
        # The actual text label with wrapping
        label = ctk.CTkLabel(
            bubble, 
            text=text, 
            text_color=text_color,
            justify="left",
            font=("Arial", 14),
            wraplength=600 # wraps text if it gets too long
        )
        label.pack(padx=15, pady=10)
        
        # If there's a file downloaded, add an actionable button
        if filepath and os.path.exists(filepath):
            btn = ctk.CTkButton(
                msg_frame, 
                text="📁 Open Download Folder", 
                width=180,
                height=32,
                fg_color="#2ba745", hover_color="#2ea043", # Green success color
                command=lambda p=filepath: self.open_file_location(p)
            )
            # Place button below the text bubble
            btn.grid(row=1, column=0, sticky="e" if is_user else "w", pady=(5,0))
            
        # Update scroll region to ensure we scroll to the bottom
        self.chat_display._parent_canvas.yview_moveto(1)

    def open_file_location(self, filepath):
        """
        Interacts with the Windows file explorer to reveal the downloaded mod.
        """
        import subprocess
        filepath = os.path.normpath(filepath)
        if os.name == 'nt':
            # Opens explorer with the file highlighted
            subprocess.run(['explorer', '/select,', filepath])

    def open_downloads_folder(self):
        """
        Opens the mods downloads folder in Windows Explorer.
        """
        import subprocess
        downloads_path = os.path.abspath('./mods')
        if not os.path.exists(downloads_path):
            os.makedirs(downloads_path, exist_ok=True)
            
        if os.name == 'nt':
            subprocess.run(['explorer', downloads_path])
        
    def send_message(self):
        """
        Triggered when user clicks 'Send' or presses Enter.
        """
        user_msg = self.msg_entry.get().strip()
        if not user_msg:
            return
            
        # 1. Clear input box to prepare for the next message
        self.msg_entry.delete(0, 'end')
        
        # 2. Add the user's message to the UI and history
        self.add_message("You", user_msg, is_user=True)
        self.chat_history.append({"role": "user", "content": user_msg})
        
        # 3. Disable send button while AI is "thinking"
        self.send_button.configure(state="disabled")
        
        # 4. Show a loading state bubble
        self.loading_frame = ctk.CTkFrame(self.chat_display, fg_color="transparent")
        self.loading_frame.grid(column=0, sticky="w", pady=5, padx=10)
        self.loading_label = ctk.CTkLabel(self.loading_frame, text="Assistant is thinking...", text_color="gray", font=("Arial", 12, "italic"))
        self.loading_label.pack(padx=15, pady=10)
        self.chat_display._parent_canvas.yview_moveto(1)

        # 5. VERY IMPORTANT: Start a new thread for the AI API call. 
        # If we don't thread this, the entire desktop app window will freeze while waiting for the LLM!
        thread = threading.Thread(target=self.process_agent_request, args=(user_msg,))
        thread.start()
        
    def process_agent_request(self, user_msg):
        """
        This runs in the background thread. We call the heavy `main.ask_agent` function here.
        """
        try:
            # Send message and history to the agent from main.py
            response = main.ask_agent(user_msg, self.chat_history)
            
            # Record assistant's response in history
            self.chat_history.append({"role": "assistant", "content": response})
            
            # Since Tkinter modifying UI from background threads can cause crashes, 
            # we use `.after(0)` to pass execution back to the main UI thread.
            self.after(0, self.display_agent_response, response, False)
        except Exception as e:
            error_msg = f"Error communicating with agent: {str(e)}"
            self.after(0, self.display_agent_response, error_msg, True)
            
    def display_agent_response(self, response, is_error=False):
        """
        This brings us back to the main UI thread to show the AI's reply.
        """
        # Remove the "thinking..." loading bubble
        if hasattr(self, 'loading_frame'):
            self.loading_frame.destroy()
            
        # Re-enable the send button
        self.send_button.configure(state="normal")
        
        if is_error:
            self.add_message("System", response, is_user=False)
            return

        # Use Regex to extract file paths (just like the previous web version did)
        # It looks for "to C:\..." or "to /..." produced by the agent when downloading
        path_match = re.search(r'to\s+([A-Za-z]:\\[^\s]+\.(?:jar|zip|exe)|/[^\s]+\.(?:jar|zip))', response)
        file_path = path_match.group(1) if path_match else None
        
        # Clean up path of stray quotes if any
        if file_path:
            file_path = file_path.strip().replace("'", "").replace('"', '')

        # Add the AI's response to the display, providing the filepath so a button gets made
        self.add_message("Assistant", response, is_user=False, filepath=file_path)

if __name__ == "__main__":
    # Launch the desktop UI loop
    app = MinecraftModApp()
    app.mainloop()
    main.save_history([]) # Clear history on exit, or you can choose to save it if you want persistence