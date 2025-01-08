import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import logging

# Utils and module references
from file_parser import Gerber_parser
from sysmlv2_api_client import SysMLv2APIClient
from utils.config_utils import save_config, load_config
from utils.json_utils import save_json, load_json

import customtkinter as ctk

# External Libraries has to be installed in the local git folder / venv 
#import requests

# Initial centralized Logging Setup to control all logs. Takes all logs from each .py file etc
def setup_logging(): 
    log_file = "app.log"
    # Remove log file if it exist to clear old content. Comment this line in case you dont want to clear old log
    if os.path.exists(log_file):
        os.remove(log_file)

    logging.basicConfig(
        level=logging.DEBUG, # Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format=" %(name)s - %(levelname)s - %(message)s", # Log format.Additional info: %(asctime)s - Line: %(lineno)d 
        handlers=[
            logging.FileHandler(log_file), # Write Logs in file 'app.log', mode="w"
            #logging.StreamHandler() # Write Logs to Console, # Comment this line to reduce clutter
        ]
    )

class SysMLv2GUI:
    """
    Main application for the GUI, managing user interaction.
    Uses Tkinter for the user interface.
    TODO
    By clicking e.g. a button the Sysmlv2GUI sends data (in form of lists, dicts, ...) to the metadata_manager.py which then maps, updates and saves the connections

    """
    def __init__(self): #, api_client
        """
        Initializes the Tkinter GUI.

        Args:
            root: The main window of the application.
        """
        self.logger = logging.getLogger(__name__)

        self.root = ctk.CTk() 
        self.root.title("SysMLv2 GUI")
        self.root.geometry("250x400")
        # Styling der GUI 
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("green")

        # Frames
        self.main_frame = ctk.CTkFrame(self.root, fg_color="lightgrey") 

        # Create GUI elements
        self.setup_widgets()
        self.setup_layout()

    def setup_widgets(self):
        """Initial creation of widgets inside the GUI."""
        self.logger.debug(f"Creating Widgets for SysMLv2GUI")

        # Button to fetch the model (get project)
        self.btn_map_data = ctk.CTkButton(self.main_frame, text="Map Data", command=self.popup_map_data)
        
        
    def setup_layout(self):
        """Sets up the layout of the GUI elements."""
        self.logger.debug(f"Setting up layout for SysMLv2GUI")
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)  
        self.root.grid_columnconfigure(0, weight=1) 
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        self.btn_map_data.grid(row=0, column=0, padx=5, pady=5, sticky="ew") 

    def popup_map_data(self):
        """Opens a popup to map the data.
        NOTE:
            - later change hardcoded file paths to user input
        """
        self.logger.debug(f"Opening popup to map data")
        popup = tk.Toplevel(self.main_frame)
        popup.title("Map Data")
        popup.geometry("1200x800")
        # Create frames for SysMLv2 and domain-specific files
        popup_left_frame = ctk.CTkFrame(popup, fg_color="lightgrey")
        popup_right_frame = ctk.CTkFrame(popup, fg_color="lightgrey")

        popup_left_frame.grid(row=1, column=0, padx=3, pady=3, sticky="nsew")
        popup_right_frame.grid(row=1, column=1, padx=3, pady=3, sticky="nsew")

        popup.grid_rowconfigure(1, weight=1)
        popup.grid_columnconfigure(0, weight=1)
        popup.grid_columnconfigure(1, weight=1)

        popup_left_frame.rowconfigure(0, weight=0)
        popup_left_frame.rowconfigure(1, weight=1)
        popup_left_frame.columnconfigure(0, weight=1)
        
        popup_right_frame.rowconfigure(0, weight=0)
        popup_right_frame.rowconfigure(1, weight=1)
        popup_right_frame.columnconfigure(0, weight=1)
        

        # Labels for the content frames
        popup_left_frame_label = ctk.CTkLabel(popup_left_frame, text="SysMLv2 File", text_color="black") 
        popup_right_frame_label = ctk.CTkLabel(popup_right_frame, text="Domain File", text_color="black")
        popup_left_frame_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        popup_right_frame_label.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Add text widgets to display file contents
        sysmlv2_file = tk.Text(popup_left_frame, wrap=tk.WORD)
        sysmlv2_file.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        domain_files = tk.Text(popup_right_frame, wrap=tk.WORD)
        domain_files.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # Load and display SysMLv2 file content
        self.load_file_content("models/se_domain/metadata_test.sysml", sysmlv2_file)
        # Load and display domain-specific file content
        self.load_file_content("models/ee_domain/Hades_project-job.gbrjob", domain_files)

        # Bind mouse click event to highlight specific words
        sysmlv2_file.bind("<Button-1>", self.highlight_words)
        domain_files.bind("<Button-1>", self.highlight_words)

    def load_file_content(self, file_path, text_widget):
        """Loads file content into the given text widget."""
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            text_widget.delete("1.0", tk.END)  # Clear previous text 
            text_widget.insert(tk.END, content)  # Write new content to text widget
        except Exception as e:
            self.logger.error(f"Failed to load file {file_path}: {e}")
            text_widget.insert(tk.END, f"Error loading file: {e}")  


    def highlight_words(self, event):
        """Highlights specific words in the text widget."""
        specific_words = ["part", "part def", "attribute", "package"]
        text_widget = event.widget
        text_widget.tag_remove("highlight", "1.0", tk.END)

        for word in specific_words:
            start_idx = "1.0"
            while True:
                start_idx = text_widget.search(word, start_idx, tk.END)
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(word)}c"
                text_widget.tag_add("highlight", start_idx, end_idx)
                start_idx = end_idx

        text_widget.tag_config("highlight", background="yellow")

    

def main(): 
    # Run Initial Log Setup
    setup_logging() 

    DEFAULT_CONFIG_FILE = "config/default_config.json" # Change config file path here 
    # Load Default Config File from config folder
    DEFAULT_CONFIG = load_config(DEFAULT_CONFIG_FILE)

    #api_client = SysMLv2APIClient(base_url=DEFAULT_CONFIG["base_url"])
    #api_client.post_model(file_path="models/se_domain/example_drone.sysml")
    #project_id = "a3ce83fe-c239-445d-8146-6fd46ceac528-"
    #api_client.get_commits(project_id=project_id)   
    #api_client.get_owned_elements(project_id=project_id, )

    #gbrjob_path = "models/ee_domain/Hades_project-job.gbrjob"
    #gerberjobfile = Gerber_parser(gbrjob_path)
    #DEFAULT_GBRJOB_SECTIONS = ["Header", "GeneralSpecs"]
    #DEFAULT_GBRJOB_KEYWORDS = ["Name", "GUID", "Version", "Vendor", "Application", "CreationDate", "X", "Y", "LayerNumber", "BoardThickness"]
    #gbrjob_metadata = gerberjobfile.parse_gerber_job_file(sections= DEFAULT_GBRJOB_SECTIONS,keywords=DEFAULT_GBRJOB_KEYWORDS)
    #print(gbrjob_metadata)



    # Start the Tkinter app
    app = SysMLv2GUI()
    app.root.mainloop() 

if __name__ == "__main__":
    main() 
