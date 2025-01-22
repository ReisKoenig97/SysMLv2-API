import tkinter as tk
from tkinter import ttk, messagebox
import os
import logging

# Utils and module references
from file_parser import GerberParser
from file_parser import SysmlParser
from sysmlv2_api_client import SysMLv2APIClient
from utils.config_utils import save_config, load_config
from utils.json_utils import save_json, load_json
from metadata_manager import MetadataManager

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

class GUI:
    """
    Main application for the GUI, managing user interaction.
    Uses Tkinter for the user interface.
    """
    def __init__(self, config, metadatamanager): 
        self.logger = logging.getLogger(__name__)
        self.config = config

        self.sysml_model = None #initialized object from sysml parser of file_parser sysml_parser
        self.sysml_model_standard_path = "" 

        self.mm = metadatamanager

        self.root = ctk.CTk() 
        self.root.title("GUI")
        self.root.geometry("250x400")
        # Styling 
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Frames
        self.main_frame = ctk.CTkFrame(self.root, fg_color="lightgrey") 

        # Create GUI elements
        self.setup_widgets()
        self.setup_layout()

    def setup_widgets(self):
        """Initial creation of widgets inside the GUI."""
        self.logger.debug(f"Creating Widgets for GUI")

        # Buttons
        self.btn_edit_sysml_model = ctk.CTkButton(self.main_frame, text="Edit SysML Model", command=self.popup_edit_sysml_model)
        self.btn_map_data = ctk.CTkButton(self.main_frame, text="Map Data", command=self.popup_map_data)  
        
    def setup_layout(self):
        """Sets up the layout of the GUI elements."""
        self.logger.debug(f"Setting up layout for GUI")
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)  
        self.root.grid_columnconfigure(0, weight=1) 
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure((0,1), weight=0)

        self.btn_edit_sysml_model.grid(row=0, column=0, padx=5, pady=(10,5), sticky="ew")
        self.btn_map_data.grid(row=1, column=0, padx=5, pady=5, sticky="ew") 

    def popup_edit_sysml_model(self):
        """Opens a popup to edit the SysML model.
        Functions: 
            - Load SysML model by user input and saves path to config file from previous session 
            - Save (Versioncontrol Git)
            - automatically searches for specific metadata format (e.g. metadata def ...)
            - Add new metadata tag
            - Delete metadata tag and tagged elements
            - Tag elements by clicking on them using the the existing metadata tag
            - Highlight tagged elements
            - Show only tagged elements by selected metadata tag 
        """

        self.logger.debug(f"Opening popup to 'popup_edit_sysml_model'")
        popup = tk.Toplevel(self.main_frame)
        popup.title("Edit SysML Model")
        popup.geometry("1200x800")
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_columnconfigure(0, weight=0)
        popup.grid_columnconfigure(1, weight=1) # 5:1 ratio for left and right frame

        # LEFT FRAME for Options to load, save, tag, delete metadata, etc.
        popup_left_frame = ctk.CTkFrame(popup, fg_color="lightgrey")
        popup_left_frame.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")
        popup_left_frame.rowconfigure((0,1,2), weight=0) 
        popup_left_frame.columnconfigure(0, weight=1)
        
        # RIGHT FRAME for displaying the SysML model
        popup_right_frame = ctk.CTkFrame(popup, fg_color="lightgrey")
        popup_right_frame.grid(row=0, column=1, padx=3, pady=3, sticky="nsew")
        popup_right_frame.rowconfigure(0, weight=0)
        popup_right_frame.rowconfigure(1, weight=1)
        popup_right_frame.columnconfigure(0, weight=1)

        # LABELS for the content frames
        popup_left_frame_label = ctk.CTkLabel(popup_left_frame, text="Options", height=30, font=("default",14), text_color="black") 
        popup_right_frame_label = ctk.CTkLabel(popup_right_frame, text="Displayed SysML Model", height=30, font=("default",14), text_color="black")

        ###### WIDGETS #####
        # User Input for SysML Model Path
        model_path_entry_label = ctk.CTkLabel(popup_left_frame, text="SysMLv2 Model Path:", font=("default", 12), text_color="black")
        model_path_entry = ctk.CTkEntry(popup_left_frame, width=150, placeholder_text="Enter SysML model path here...")
        self.sysml_model_standard_path = os.path.join(self.config["base_se_path"], self.config["base_se_model"])
        model_path_entry.insert(0,self.sysml_model_standard_path) # Insert into entry widget 
        sysml_file_text_widget = tk.Text(popup_right_frame, wrap=tk.WORD)
        # lambda is used to make sure that the function is called when the button is pressed 
        btn_load_model = ctk.CTkButton(popup_left_frame, text="Load", width=100,
                                       command=lambda: self.load_model_path_preference(entry_widget=model_path_entry, text_widget=sysml_file_text_widget, model_type="sysml")) 
        
        # Button to parse and highlight elements that are tagged with a specific structure (here: '@<name> about')
        btn_highlight_tagged_elements_by_metadata = ctk.CTkButton(popup_left_frame, text="Highlight", width=100,
                                                                  command=lambda: self.highlight_tagged_elements_by_metadata(text_widget=sysml_file_text_widget, entry_widget=model_path_entry)) 
        

        # LEFT FRAME GRID LAYOUT 
        popup_left_frame_label.grid(row=0, column=0, columnspan=2, pady=2, sticky="ew")
        model_path_entry_label.grid(row=1, column=0, padx=10, pady=5, sticky="w") #pady=(10, 5) 
        model_path_entry.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        btn_load_model.grid(row=2, column=1, padx=(5, 5), pady=(0, 10), sticky="w")
        btn_highlight_tagged_elements_by_metadata.grid(row=3, column=1, padx=(5, 5), pady=(0, 10), sticky="news") 

        # RIGHT FRAME GRID LAYOUT 
        popup_right_frame_label.grid(row=0, column=0, pady=2, sticky="ew") 
        sysml_file_text_widget.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")   

    def highlight_tagged_elements_by_metadata(self, text_widget, entry_widget, highlight_nested_element = True):
        """Parses and highlights elements by metadata inside the 'popup_edit_sysml_model' 
        Uses file_parser.py with the Sysml_parser class for function usage
        1) Checks if certain metadata structure (look up file_parser.py) is given inside the sysml file or not 
        2) Parses and highlights sysml file to search for given metadata and metadata about paths
        Uses:
            sysml_parser class functions
                check_metadata_exist 

        Parameters:
            highlight_nested_element : Boolean. Flag to show/don't show nested elements (starting/ending from '{...}')
                                                Default = True 
                                    
        Returns: Adjusted ctk.Text Widget with highlighted elements 
        """
        # Get the current user given sysml path 
        self.sysml_model_standard_path = entry_widget.get()
        # Check if sysml model full path is not None:
        if self.sysml_model_standard_path: 
            self.logger.debug(f"Found valid sysml model path: {self.sysml_model_standard_path}")

            try: 
                # Create sysml_parser class to get class functions 
                self.sysml_model = SysmlParser(sysml_path=self.sysml_model_standard_path)
                self.logger.debug(f"Successfully created sysml_parser class instance")
                # Check if sysml model has a certain metadata structure 
                found_metadata = self.sysml_model.check_metadata_exist()

                # Check if found_metadata (list) is not empty
                if found_metadata: 
                    self.logger.debug(f"Found Metadata: {found_metadata}")
                    sysml_file_content = self.load_file_content(file_path=entry_widget.get(), text_widget=text_widget)

                    # Loop through every metadata def name
                    for metadata in found_metadata:
                        metadata_about_tags = self.sysml_model.get_metadata_about_elements(metadata_name=metadata)
                        if sysml_file_content:
                            self.logger.debug(f"SysML file content loaded.")
                            lines = sysml_file_content.splitlines()

                            inside_nested_block = False  # Tracks whether we're inside a nested block
                            nested_start_line = 0  # Stores the start line of a nested block

                            for line_num, line in enumerate(lines, start=1): 
                                for about_tag in metadata_about_tags:  
                                    if about_tag in line:
                                        self.logger.debug(f"Found {about_tag} in line: {line}")
                                        start_index = f"{line_num}.0"
                                        end_index = f"{line_num}.end"
                                        text_widget.tag_add("highlight", start_index, end_index)
                                        text_widget.tag_config("highlight", background="yellow", foreground="black")
                                        self.logger.debug(f"Highlighted keyword: {about_tag} on line {line_num}")
                                        
                                        # Start nested block tracking
                                        if highlight_nested_element and "{" in line:
                                            inside_nested_block = True
                                            nested_start_line = line_num

                                # Handle nested elements spanning multiple lines
                                if inside_nested_block:
                                    if "{" in line and line_num == nested_start_line:
                                        continue  # Skip starting line, already handled
                                    
                                    nested_start_index = f"{line_num}.0"
                                    nested_end_index = f"{line_num}.end"
                                    text_widget.tag_add("highlight", nested_start_index, nested_end_index)
                                    self.logger.debug(f"Highlighted nested content on line {line_num}")

                                    # End nested block when encountering closing brace
                                    if "}" in line:
                                        inside_nested_block = False

            except Exception as e: 
                self.logger.info(f"Error trying to create a sysml_parser class instance with error: {e}")
    
    def load_model_path_preference(self, entry_widget, text_widget, model_type):
        """Loads the SysML model, using the provided Entry widget and Text widget.
        
        Parameters: 
            model_type : String. Indicates which domain should be loaded. ("sysml" or "domain")

        """
        self.logger.debug(f"Loading Model with type: {model_type}")
        user_path = entry_widget.get().strip()
        self.logger.debug(f"Selected user path: {user_path}")

        # If user provides a path, prioritize it; otherwise, use default from config
        if user_path and os.path.exists(user_path):
            self.logger.info(f"Using user-provided path: '{user_path}'")
            if model_type == "sysml":
                self.logger.debug(f"Found type: sysml")
                self.sysml_model_standard_path = user_path
            if model_type == "domain": 
                self.logger.debug(f"Found type domain")
                self.domain_model_standard_path = user_path
        else:
            self.logger.warning(f"User-provided path is invalid or empty.")

        # Load the file into the text widget
        self.load_file_content(file_path=user_path, text_widget=text_widget)

    def popup_map_data(self):
        """Opens a popup to map the data.
        """
        self.logger.debug(f"Opening popup to map data")
        popup = tk.Toplevel(self.main_frame)
        popup.title("Map Data")
        popup.geometry("1500x1000")
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_rowconfigure(1, weight=0)
        popup.grid_columnconfigure(0, weight=0) #weight 0 means as much as it needs 
        popup.grid_columnconfigure((1,2), weight=1)

        ########## FRAMES ##########
        # OPTIONS FRAME
        options_frame = ctk.CTkFrame(popup, fg_color="lightgrey")
        options_frame.rowconfigure(0, weight=0)
        options_frame.rowconfigure(1, weight=0)
        options_frame.columnconfigure(0, weight=0)
        options_frame.columnconfigure(1, weight=0)

        # SYSML FRAME: LEFT
        sysml_frame = ctk.CTkFrame(popup, fg_color="lightgrey")
        sysml_frame.rowconfigure(0, weight=0) # Used for label with set custom height 
        sysml_frame.rowconfigure(1, weight=1)
        sysml_frame.columnconfigure(0, weight=1)

        # DOMAIN FRAME: RIGHT
        domain_frame = ctk.CTkFrame(popup, fg_color="lightgrey")
        domain_frame.rowconfigure(0, weight=0)
        domain_frame.rowconfigure(1, weight=1)
        domain_frame.columnconfigure(0, weight=1)

        # MAP FRAME 
        map_frame = ctk.CTkFrame(popup, fg_color="lightgrey")
        map_frame.rowconfigure((0,1,2,3,4,5),weight=1)
        map_frame.columnconfigure((0,1,2,3), weight=1)

        # GENERAL POPUP LAYOUT 
        options_frame.grid(row=0, column=0, rowspan=2, padx=3, pady=3, sticky="news") #left side
        sysml_frame.grid(row=0, column=1, padx=3, pady=3, sticky="nsew") 
        domain_frame.grid(row=0, column=2, padx=3, pady=3, sticky="nsew")
        map_frame.grid(row=1, column=1 ,columnspan=2, padx=3, pady=3, sticky="news")


        # Labels for frames 
        sysml_frame_label = ctk.CTkLabel(sysml_frame, text="SysMLv2 File", height=30, font=("default",14), text_color="black") 
        domain_frame_label = ctk.CTkLabel(domain_frame, text="Domain File", height=30, font=("default",14), text_color="black")
        options_frame_label = ctk.CTkLabel(options_frame, text="Options", height=30, font=("default",14), text_color="black")
        map_frame_label = ctk.CTkLabel(map_frame, text="Map Elements", height=30, font=("default", 14), text_color="black")

        
        ########## WIDGETS ########## 

        # SYSML FRAME:      Label, Entry, Text and Button for user input to load sysml model 
        options_frame_sysml_path_entry_label = ctk.CTkLabel(options_frame, text="SysMLv2 Model Path:",
                                                             font=("default",12),text_color="black")
        options_frame_sysml_path_entry = ctk.CTkEntry(options_frame, width=150, 
                                                      placeholder_text="Enter SysML model path here...")
        self.sysml_model_standard_path = os.path.join(self.config["base_se_path"], self.config["base_se_model"])
        options_frame_sysml_path_entry.insert(0, self.sysml_model_standard_path)
        sysml_frame_model_text_widget = tk.Text(sysml_frame, wrap=tk.WORD)
        btn_load_model_sysml = ctk.CTkButton(options_frame, text="Load SysML Model", width=50,
                                             command=lambda: self.load_model_path_preference(entry_widget=options_frame_sysml_path_entry, text_widget=sysml_frame_model_text_widget, model_type="sysml"))
        # DOMAIN FRAME:     Label, Entry, Text and Button for user input to load domain model 
        options_frame_domain_file_format_entry_label = ctk.CTkLabel(options_frame, text="Domain File Format",
                                                        font=("default", 12), text_color="black")
        options_frame_domain_file_format_entry = ctk.CTkEntry(options_frame, width=150,
                                                              placeholder_text="Enter Domain File Format e.g. GerberJobFile")
        options_frame_domain_path_entry_label = ctk.CTkLabel(options_frame, text="Domain Model Path:",
                                                             font=("default",12),text_color="black")
        options_frame_domain_path_entry = ctk.CTkEntry(options_frame, width=150, 
                                                       placeholder_text="Enter Domain model path here...")
        self.domain_model_standard_path = os.path.join(self.config["base_ee_path"],self.config["base_ee_model"])
        options_frame_domain_path_entry.insert(0, self.domain_model_standard_path)
        domain_frame_model_text_widget = tk.Text(domain_frame, wrap=tk.WORD)
        btn_load_model_domain = ctk.CTkButton(options_frame, text="Load Domain Model", width=50,
                                              command=lambda: self.load_model_path_preference(entry_widget=options_frame_domain_path_entry, text_widget=domain_frame_model_text_widget, model_type="domain"))
        # MAP FRAME:        Labels, Entries and Button for user input to connect elements
        map_frame_sysml_name_label = ctk.CTkLabel(map_frame, text="SysML Element Path:", 
                                                  font=("default", 12), text_color="black")
        map_frame_sysml_name_entry = ctk.CTkEntry(map_frame, placeholder_text="Enter a sysml element path e.g 'package.partA.len'")
        map_frame_sysml_value_label = ctk.CTkLabel(map_frame, text="SysML Element Value:",
                                                   font=("default", 12), text_color="black")
        map_frame_sysml_value_entry = ctk.CTkEntry(map_frame, placeholder_text="Enter corresponding element value e.g. 50")
        map_frame_domain_name_label = ctk.CTkLabel(map_frame, text="Domain Element Path:",
                                                   font=("default", 12), text_color="black")
        map_frame_domain_name_entry = ctk.CTkEntry(map_frame, placeholder_text="Enter a domain element path e.g. 'GeneralSpecs.Size.X'")
        map_frame_domain_value_label = ctk.CTkLabel(map_frame, text="Domain Element Value:",
                                                    font=("default", 12), text_color="black") 
        map_frame_domain_value_entry = ctk.CTkEntry(map_frame, placeholder_text="Enter corresponding element value e.g. '7.42'")

        btn_map_elements = ctk.CTkButton(map_frame, text="Map elements", width=100, 
                                         command=lambda: self.map_elements(options_frame_sysml_path_entry,
                                                                   map_frame_sysml_name_entry,
                                                                   map_frame_sysml_value_entry,
                                                                   options_frame_domain_file_format_entry,
                                                                   options_frame_domain_path_entry, 
                                                                   map_frame_domain_name_entry, 
                                                                   map_frame_domain_value_entry))

        ########## LAYOUT ##########

        # OPTIONS FRAME LAYOUT 
        #   Load sysml model 
        options_frame_label.grid(row=0, column=0, columnspan=2, pady=2, sticky="ew") 
        options_frame_sysml_path_entry_label.grid(row=1, column=0, padx=5, pady=(2,0), sticky="w") 
        options_frame_sysml_path_entry.grid(row=2, column=0, padx=5, pady=(5,0), sticky="ew")
        btn_load_model_sysml.grid(row=2, column=1, padx=(5, 5), pady=(5, 0), sticky="ew") 
        #   Load domain model 
        options_frame_domain_file_format_entry_label.grid(row=3, column=0, padx=5, pady=(5,0), sticky="w")
        options_frame_domain_file_format_entry.grid(row=4, column=0, padx=5, pady=(2,0), sticky="w") 
        options_frame_domain_path_entry_label.grid(row=5, column=0, padx=5, pady=(5,0), sticky="w")
        options_frame_domain_path_entry.grid(row=6, column=0, padx=5, pady=(2,0), sticky="ew")
        btn_load_model_domain.grid(row=6, column=1, padx=(5, 5), pady=(5, 0), sticky="ew")

        # SYSML FRAME LAYOUT 
        sysml_frame_label.grid(row=0, column=0, pady=2, sticky="ew") 
        sysml_frame_model_text_widget.grid(row=1, column=0, padx=5, pady=5, sticky="nsew") 

        # DOMAIN FRAME LAYOUT 
        domain_frame_label.grid(row=0, column=0, pady=2, sticky="ew")
        domain_frame_model_text_widget.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        # MAP FRAME LAYOUT 
        map_frame_label.grid(row=0, column=0, columnspan=4, pady=2, sticky="ew")
        map_frame_sysml_name_label.grid(row=1, column=0, columnspan=2, padx=(10,5), pady=(5,0), sticky="w")
        map_frame_sysml_name_entry.grid(row=2, column=0, columnspan=2, padx=(10,5), pady=(2,0), sticky="ew")
        map_frame_sysml_value_label.grid(row=3, column=0, columnspan=2, padx=(10,5), pady=(5,0), sticky="w")
        map_frame_sysml_value_entry.grid(row=4, column=0, columnspan=2, padx=(10,5), pady=(2,5), sticky="ew")
        
        map_frame_domain_name_label.grid(row=1, column=2, columnspan=2, padx=(5,10), pady=(5,0), sticky="w")
        map_frame_domain_name_entry.grid(row=2, column=2, columnspan=2, padx=(5,10), pady=(2,5), sticky="ew")
        map_frame_domain_value_label.grid(row=3, column=2, columnspan=2, padx=(5,10), pady=(5,0), sticky="w")
        map_frame_domain_value_entry.grid(row=4, column=2, columnspan=2, padx=(5,10), pady=(2,5), sticky="ew")

        btn_map_elements.grid(row=5, column=1, columnspan=2, padx=(5,5), pady=(10,10), sticky="ew")
        
    def load_file_content(self, file_path, text_widget):
        """Loads file content into the given text widget."""
        self.logger.debug(f"Loading file content from file path: {file_path}")
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            text_widget.delete("1.0", tk.END)  # Clear previous text 
            text_widget.insert(tk.END, content)  # Write new content to text widget
            return content 
        except Exception as e:
            self.logger.error(f"Failed to load file {file_path}: {e}")
            text_widget.delete("1.0", tk.END)  # Clear previous text 
            text_widget.insert(tk.END, f"Error loading file: {e}")  

    def map_elements(self, sysml_path, sysml_element_path, sysml_element_value, domain_file_format, domain_path, domain_element_path, domain_element_value): 
        # TODO: Use and reference functions from class METADATA MANAGER! 
        """
        - metadata_manager has to parse file via file_parser functions to get specific user given path to the element in order to generate UUID and map correctly 
        
        """
        self.logger.debug(f"Mapping selected elements")
        sysml_path = sysml_path.get()
        #self.logger.debug(f"User provided sysml path inside entry: {sysml_path}")
        sysml_element_path = sysml_element_path.get()
        sysml_element_value = sysml_element_value.get()
        domain_file_format = domain_file_format.get() 
        domain_path = domain_path.get()
        domain_element_path = domain_element_path.get()
        domain_element_value = domain_element_value.get()
        #Initialize SysmlParser analog to 'popup_edit_sysml_model'
        self.sysml_model = SysmlParser(sysml_path=sysml_path) 
        # Validate user given element path (function from file parser)
        if not self.sysml_model.validate_element_path(element_path=sysml_element_path): 
            self.logger.info(f"User provided an invalid sysml element pathing: {sysml_element_path}")
            messagebox.showinfo("INFO", "Provided SysML element path is invalid.")

        else:
            if self.mm.map_metadata(sysml_path, sysml_element_path, sysml_element_value, domain_file_format, domain_path, domain_element_path, domain_element_value):
                # Notify the user about the successful mapping
                messagebox.showinfo("INFO", "Successfully mapped elements together!")
                # Show the mapped elements in a new popup
                def show_mapping_popup():
                    popup = tk.Toplevel()
                    popup.title("Mapped Elements")
                    
                    # Create labels for SysML and Domain elements
                    label = ctk.CTkLabel(popup, text="Mapped Elements", font=("Arial", 14, "bold"), text_color="black")
                    label.pack(pady=10)
                    sysml_label = ctk.CTkLabel(popup, text=f"SysML Element: {sysml_element_path} : {sysml_element_value}", font=("Arial", 12), text_color="black")
                    sysml_label.pack(pady=5)
                    domain_label = ctk.CTkLabel(popup, text=f"Domain Element: {domain_element_path}: {domain_element_value}", font=("Arial", 12), text_color="black")
                    domain_label.pack(pady=5)
                    # Close button for the popup
                    # close_button = ctk.CTkButton(popup, text="OK", fg="blue", cursor="hand2")
                    # close_button.pack(pady=10)
                    # close_button.bind("<Button-1>", lambda e: popup.destroy())
                
                # Call the mapping popup function
                show_mapping_popup()
            else:
                # Notify the user about the failure of mapping
                messagebox.showerror


def main(): 
    # Run Initial Log Setup for debugging
    setup_logging() 
    # Load Default Config File from config folder   
    DEFAULT_CONFIG_FILE = "config/default_config.json" 
    DEFAULT_CONFIG = load_config(DEFAULT_CONFIG_FILE)

    mm = MetadataManager(config=DEFAULT_CONFIG) 

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
    app = GUI(config=DEFAULT_CONFIG, metadatamanager = mm)
    app.root.mainloop() 

if __name__ == "__main__":
    main() 
