import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import StringVar # used for Dropdown menus 
from tkinter import filedialog # used for loading files via file explorer of the OS 
import os
import logging

# Utils and module references
from file_parser import GerberParser
from file_parser import SysmlParser
from file_parser import StepParser
from file_parser import CodeParser

from sysmlv2_api_client import SysMLv2APIClient
from utils.config_utils import save_config, load_config
from utils.json_utils import save_json, load_json
from metadata_manager import MetadataManager
from versioncontrol import VersionControl 

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
    def __init__(self, config, metadatamanager=None, versioncontrol=None): 
        self.logger = logging.getLogger(__name__ + "-GUI")
       
        self.config = config
        # List acts as the accepted file formats (used inside the map popup)
        self.available_file_formats = ["GerberJobFile", "STEP", "Source Code"]
        # List for available datatypes and si units
        self.available_datatypes = ["int", "float", "string", "bool"]
        self.available_units = ["", "m", "kg", "s", "A", "K", "mol", "m^2", "m^3", "N", "Pa", "J", "W", "C", "V", "F"]

        self.sysml_model = None #initialized object from sysml parser of file_parser sysml_parser
        self.sysml_file_path = ""
        self.domain_file_path = ""

        self.mm = metadatamanager
        self.vc = versioncontrol

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
        #self.logger.info(f"setup_widgets")

        # Buttons
        self.btn_edit_sysml_model = ctk.CTkButton(self.main_frame, text="View/Edit SysML Model", command=self.popup_edit_sysml_model)
        self.btn_map_data = ctk.CTkButton(self.main_frame, text="Map Data", command=self.popup_map_data)  
        self.btn_version_control = ctk.CTkButton(self.main_frame, text="Version Control", command=self.popup_version_control)
        self.btn_verification = ctk.CTkButton(self.main_frame, text="Verification Analysis", command=self.popup_verification)
        
    def setup_layout(self):
        """Sets up the layout of the GUI elements."""
        #self.logger.info(f"setup_layout")
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)  
        self.root.grid_columnconfigure(0, weight=1) 
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure((0,1), weight=0)

        self.btn_edit_sysml_model.grid(row=0, column=0, padx=5, pady=(10,5), sticky="ew")
        self.btn_map_data.grid(row=1, column=0, padx=5, pady=5, sticky="ew") 
        self.btn_version_control.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
        self.btn_verification.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

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

        #self.logger.info(f"popup_edit_sysml_model")
        popup = tk.Toplevel(self.main_frame)
        popup.title("Edit SysML Model")
        popup.geometry("1000x800")
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_columnconfigure(0, weight=0)
        popup.grid_columnconfigure(1, weight=1) # 5:1 ratio for left and right frame
        
        # RIGHT FRAME for displaying the SysML model
        display_frame = ctk.CTkFrame(popup, fg_color="lightgrey")
        display_frame.grid(row=0, column=1, padx=3, pady=3, sticky="nsew")
        display_frame.rowconfigure(0, weight=0)
        display_frame.rowconfigure(1, weight=1)
        display_frame.columnconfigure(0, weight=1)
        display_frame.columnconfigure((1,2), weight=0)

        # LABELS for the content frames
        display_frame_label = ctk.CTkLabel(display_frame, text="SysMLv2 File", height=30, font=("default",14), text_color="black")

        ###### WIDGETS #####
        # User Input for SysML Model Path
        sysml_file_text_widget = tk.Text(display_frame, wrap=tk.WORD)                          
        btn_load_model = ctk.CTkButton(display_frame, text="Load SysMLv2 Model", width=100, command=lambda: self.select_file(model_type="sysml", text_widget=sysml_file_text_widget))


        # Button to parse and highlight elements that are tagged with a specific structure (here: '@<name> about')
        btn_highlight_tagged_elements_by_metadata = ctk.CTkButton(display_frame, text="Highlight elements by metadata", width=100,
                                                                  command=lambda: self.highlight_tagged_elements_by_metadata(text_widget=sysml_file_text_widget)) 
        
        ###### LAYOUT ######
        btn_load_model.grid(row=0, column=1, padx=(5, 5), pady=(5,0), sticky="ew")
        btn_highlight_tagged_elements_by_metadata.grid(row=0, column=2, padx=(5, 5), pady=(5,0), sticky="ew") 

        # RIGHT FRAME GRID LAYOUT 
        display_frame_label.grid(row=0, column=0, pady=(5,0), sticky="ew") 
        sysml_file_text_widget.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")   

    def highlight_tagged_elements_by_metadata(self, text_widget, highlight_nested_element = True):
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
        #self.logger.info(f"highlight_tagged_elements_by_metadata")
        # Get the current user given sysml path 
        
        # Check if sysml model full path is not None:
        if self.sysml_file_path: 
            #self.logger.debug(f"Found valid sysml model path: {self.sysml_file_path}")

            try: 
                # Create sysml_parser class to get class functions 
                self.sysml_model = SysmlParser(sysml_path=self.sysml_file_path)
                #self.logger.debug(f"Successfully created sysml_parser class instance")
                # Check if sysml model has a certain metadata structure 
                found_metadata = self.sysml_model.check_metadata_exist()

                # Check if found_metadata (list) is not empty
                if found_metadata: 
                    #self.logger.debug(f"Found Metadata: {found_metadata}")
                    sysml_file_content = self.load_file_content(file_path=self.sysml_file_path, text_widget=text_widget)

                    # Loop through every metadata def name
                    for metadata in found_metadata:
                        metadata_about_tags = self.sysml_model.get_metadata_about_elements(metadata_name=metadata)
                        if sysml_file_content:
                            #self.logger.debug(f"SysML file content loaded.")
                            lines = sysml_file_content.splitlines()

                            inside_nested_block = False  # Tracks whether we're inside a nested block
                            nested_start_line = 0  # Stores the start line of a nested block

                            for line_num, line in enumerate(lines, start=1): 
                                for about_tag in metadata_about_tags:  
                                    if about_tag in line:
                                        #self.logger.debug(f"Found {about_tag} in line: {line}")
                                        start_index = f"{line_num}.0"
                                        end_index = f"{line_num}.end"
                                        text_widget.tag_add("highlight", start_index, end_index)
                                        text_widget.tag_config("highlight", background="yellow", foreground="black")
                                        #self.logger.debug(f"Highlighted keyword: {about_tag} on line {line_num}")
                                        
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
                                    #self.logger.debug(f"Highlighted nested content on line {line_num}")

                                    # End nested block when encountering closing brace
                                    if "}" in line:
                                        inside_nested_block = False

            except Exception as e: 
                self.logger.info(f"Error trying to create a sysml_parser class instance with error: {e}")

    def popup_map_data(self):
        """Opens a popup to map the data.
        """
        #self.logger.info(f"popup_map_data")
        popup = tk.Toplevel(self.main_frame)
        popup.title("Map Data")
        popup.geometry("1500x1000")
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_rowconfigure(1, weight=0)
        popup.grid_columnconfigure(0, weight=1) #weight 0 means as much as it needs 
        popup.grid_columnconfigure(1, weight=1) #(1,2)

        ########## FRAMES ##########
        # SYSML FRAME: LEFT
        sysml_frame = ctk.CTkFrame(popup, fg_color="lightgrey")
        sysml_frame.rowconfigure(0, weight=0) # Used for label with set custom height 
        sysml_frame.rowconfigure(1, weight=1)
        sysml_frame.columnconfigure(0, weight=1)
        sysml_frame.columnconfigure(1, weight=1)
        # DOMAIN FRAME: RIGHT
        domain_frame = ctk.CTkFrame(popup, fg_color="lightgrey")
        domain_frame.rowconfigure(0, weight=0)
        domain_frame.rowconfigure(1, weight=1)
        domain_frame.columnconfigure(0, weight=1)
        domain_frame.columnconfigure((1,2), weight=0)
        # MAP FRAME 
        map_frame = ctk.CTkFrame(popup, fg_color="lightgrey")
        map_frame.rowconfigure((0,1,2,3,4,5),weight=1)
        map_frame.columnconfigure((0,1,2,3), weight=1)

        # POPUP LAYOUT 
        sysml_frame.grid(row=0, column=0, padx=3, pady=3, sticky="nsew") 
        domain_frame.grid(row=0, column=1, columnspan=3, padx=3, pady=3, sticky="nsew")
        map_frame.grid(row=1, column=0 ,columnspan=2, padx=3, pady=3, sticky="news")

        ########## WIDGETS ########## 
        sysml_frame_label = ctk.CTkLabel(sysml_frame, text="SysMLv2 File", height=30, font=("default",14), text_color="black") 
        domain_frame_label = ctk.CTkLabel(domain_frame, text="Domain File", height=30, font=("default",14), text_color="black")
        map_frame_label = ctk.CTkLabel(map_frame, text="Map Elements", height=30, font=("default", 14), text_color="black")

        sysml_frame_text_widget = tk.Text(sysml_frame, wrap=tk.WORD)
        btn_load_model_sysml = ctk.CTkButton(sysml_frame, text="Load SysML Model", command=lambda: self.select_file(model_type="sysml", text_widget=sysml_frame_text_widget))
        
        selected_domain_format = StringVar(value=self.available_file_formats[0]) #[0] first element is the default value
        domain_file_format_dropdown = ctk.CTkOptionMenu(domain_frame, values=self.available_file_formats,variable=selected_domain_format)
        domain_frame_text_widget = tk.Text(domain_frame, wrap=tk.WORD)
        btn_load_model_domain = ctk.CTkButton(domain_frame, text="Load Domain Model", 
                                             command=lambda: self.select_file(model_type="domain", text_widget=domain_frame_text_widget))
        # MAP FRAME:        Labels, Entries and Button for user input to connect elements
        map_frame_sysml_name_label = ctk.CTkLabel(map_frame, text="SysML Element Path:", font=("default", 12), text_color="black")
        map_frame_sysml_name_entry = ctk.CTkEntry(map_frame, placeholder_text="Enter a sysml element path e.g 'package.partA.len'")
        map_frame_sysml_value_label = ctk.CTkLabel(map_frame, text="SysML Element Value:",font=("default", 12), text_color="black")
        map_frame_sysml_value_entry = ctk.CTkEntry(map_frame, placeholder_text="Enter corresponding element value e.g. 50")
        selected_sysml_element_unit = StringVar(value=self.available_units[0]) # initial value
        map_frame_sysml_unit_dropdown = ctk.CTkOptionMenu(map_frame, values=self.available_units,variable=selected_sysml_element_unit)
        map_frame_sysml_unit_dropdown_label = ctk.CTkLabel(map_frame, text="SysML Element Unit (if possible):",font=("default", 12), text_color="black")
        
        map_frame_domain_name_label = ctk.CTkLabel(map_frame, text="Domain Element Path:", font=("default", 12), text_color="black")
        map_frame_domain_name_entry = ctk.CTkEntry(map_frame, placeholder_text="Enter a domain element path e.g. 'GeneralSpecs.Size.X'")
        map_frame_domain_value_label = ctk.CTkLabel(map_frame, text="Domain Element Value:", font=("default", 12), text_color="black") 
        map_frame_domain_value_entry = ctk.CTkEntry(map_frame, placeholder_text="Enter corresponding element value e.g. '7.42'")
        selected_domain_element_unit = StringVar(value=self.available_units[0]) # initial value as default 
        map_frame_domain_unit_dropdown = ctk.CTkOptionMenu(map_frame, values=self.available_units, variable=selected_domain_element_unit)
        map_frame_domain_unit_dropdown_label = ctk.CTkLabel(map_frame, text="Domain Element Unit (if possible):", font=("default", 12), text_color="black")

        btn_map_elements = ctk.CTkButton(map_frame, text="Map elements", width=100, 
                                         command=lambda: self.map_elements(self.sysml_file_path,
                                                                   map_frame_sysml_name_entry,
                                                                   map_frame_sysml_value_entry,
                                                                   selected_sysml_element_unit,
                                                                   selected_domain_format,
                                                                   self.domain_file_path, 
                                                                   map_frame_domain_name_entry, 
                                                                   map_frame_domain_value_entry,
                                                                   selected_domain_element_unit))

        ########## LAYOUT ##########
        # SYSML FRAME LAYOUT 
        sysml_frame_label.grid(row=0, column=0, padx=5, pady=(5,0), sticky="news") 
        sysml_frame_text_widget.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew") 
        btn_load_model_sysml.grid(row=0, column=1, padx=5, pady=(5,0), sticky="e") 
        # DOMAIN FRAME LAYOUT 
        domain_frame_label.grid(row=0, column=0, pady=(5,0), sticky="ew")
        domain_frame_text_widget.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")
        domain_file_format_dropdown.grid(row=0, column=1, padx=(5,5), pady=(5,0), sticky="ew") #padx = 5 
        btn_load_model_domain.grid(row=0, column=2, padx=(5, 5), pady=(5, 0), sticky="ew")
        # MAP FRAME LAYOUT 
        map_frame_label.grid(row=0, column=0, columnspan=4, pady=2, sticky="ew")
        map_frame_sysml_name_label.grid(row=1, column=0, columnspan=2, padx=(10,5), pady=(5,0), sticky="w")
        map_frame_sysml_name_entry.grid(row=2, column=0, columnspan=2, padx=(10,5), pady=(2,0), sticky="ew")
        map_frame_sysml_value_label.grid(row=3, column=0, columnspan=2, padx=(10,5), pady=(5,0), sticky="w")
        map_frame_sysml_value_entry.grid(row=4, column=0, columnspan=2, padx=(10,5), pady=(2,5), sticky="ew")
        map_frame_sysml_unit_dropdown_label.grid(row=5, column=0, columnspan=2, padx=(10,5), pady=(5,0), sticky="w")
        map_frame_sysml_unit_dropdown.grid(row=6, column=0, columnspan=2, padx=(10,5), pady=(2,5), sticky="ew")

        map_frame_domain_name_label.grid(row=1, column=2, columnspan=2, padx=(5,10), pady=(5,0), sticky="w")
        map_frame_domain_name_entry.grid(row=2, column=2, columnspan=2, padx=(5,10), pady=(2,5), sticky="ew")
        map_frame_domain_value_label.grid(row=3, column=2, columnspan=2, padx=(5,10), pady=(5,0), sticky="w")
        map_frame_domain_value_entry.grid(row=4, column=2, columnspan=2, padx=(5,10), pady=(2,5), sticky="ew")
        map_frame_domain_unit_dropdown_label.grid(row=5, column=2, columnspan=2, padx=(5,10), pady=(5,0), sticky="w")
        map_frame_domain_unit_dropdown.grid(row=6, column=2, columnspan=2, padx=(5,10), pady=(2,5), sticky="ew")

        btn_map_elements.grid(row=7, column=1, columnspan=2, padx=(5,5), pady=(10,10), sticky="ew")

    def select_file(self, model_type, text_widget):
        """ 
        Opens a file dialog to select a SysML file inside the file explorer of the OS 
        """ 
        #self.logger.info(f"select_file")
        if model_type == "sysml":
            filetypes = [("SysML files", "*.sysml")]
        else:
            filetypes = [("All files", "*.*")]
        filepath = filedialog.askopenfilename(title=f"Select a {model_type.capitalize()} File", filetypes=filetypes) #,("SysML files", "*.sysml")
        
        if filepath: 
            if model_type == "sysml": 
                self.sysml_file_path = filepath 
            else:
                self.domain_file_path = filepath
                
            self.load_file_content(file_path=filepath, text_widget=text_widget)
            
    def load_file_content(self, file_path, text_widget):
        """Loads file content into the given text widget."""
        self.logger.info(f"load_file_content")
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

    def map_elements(self, sysml_path, sysml_element_path, sysml_element_value, sysml_element_unit, domain_file_format, domain_path, domain_element_path, domain_element_value, domain_element_unit): 
        # TODO: Use and reference functions from class METADATA MANAGER! 
        """
        - metadata_manager has to parse file via file_parser functions to get specific user given path to the element in order to generate UUID and map correctly 
        
        """
        #self.logger.info(f"map_elements")
        # sysml_path = sysml_path.get()
        #self.logger.debug(f"User provided sysml path inside entry: {sysml_path}")
        sysml_element_path = sysml_element_path.get()
        sysml_element_value = sysml_element_value.get()
        sysml_element_unit = sysml_element_unit.get()
        domain_file_format = domain_file_format.get() 
        # domain_path = domain_path.get()
        domain_element_path = domain_element_path.get()
        domain_element_value = domain_element_value.get()
        domain_element_unit = domain_element_unit.get()
        #Initialize SysmlParser analog to 'popup_edit_sysml_model'
        self.sysml_model = SysmlParser(sysml_path=sysml_path) 
        #self.logger.debug(f"Created SysML Parser instance: {self.sysml_model}")
        # Validate user given element path (function from file parser)
        if not self.sysml_model.validate_elementPath(elementPath=sysml_element_path): 
            self.logger.warning(f"User provided an invalid sysml element pathing: {sysml_element_path}")
            messagebox.showinfo("INFO", "Provided SysML element path is invalid.")

        else:
            if self.mm.map_metadata(sysml_path, sysml_element_path, sysml_element_value, sysml_element_unit, domain_file_format, domain_path, domain_element_path, domain_element_value, domain_element_unit):
                # Notify the user about the successful mapping
                messagebox.showinfo("INFO", "Successfully mapped elements together!")
                # Show the mapped elements in a new popup
                # UNCOMMENT IF NEEDED
                # def show_mapping_popup():
                #     popup = tk.Toplevel()
                #     popup.title("Mapped Elements")
                    
                #     # Create labels for SysML and Domain elements
                #     label = ctk.CTkLabel(popup, text="Mapped Elements", font=("Arial", 14, "bold"), text_color="black")
                #     label.pack(pady=10)
                #     sysml_label = ctk.CTkLabel(popup, text=f"SysML Element: {sysml_element_path} : {sysml_element_value}", font=("Arial", 12), text_color="black")
                #     sysml_label.pack(pady=5)
                #     domain_label = ctk.CTkLabel(popup, text=f"Domain Element: {domain_element_path}: {domain_element_value}", font=("Arial", 12), text_color="black")
                #     domain_label.pack(pady=5)
                #     # Close button for the popup
                #     # close_button = ctk.CTkButton(popup, text="OK", fg="blue", cursor="hand2")
                #     # close_button.pack(pady=10)
                #     # close_button.bind("<Button-1>", lambda e: popup.destroy())
            
                # # Call the mapping popup function
                # show_mapping_popup()

            else:
                # Notify the user about the failure of mapping
                messagebox.showerror(f"ERROR", "Cannot map metadata.")

    def popup_version_control(self): 
        """Opens a popup where the user can select different commits and versions of a selected file 
        and can see the history of changes 
        Assumptions: User wants to see changes between latest and selected commit (all shown commits are previous ones)
        NOTE: 
            1) User selects file path (therefore user compares changes to (latest) model file)
            2) script loads the commit history inside the treeview widget
            3) after selection and Button press
            4) Display git diff 
        """
        #self.logger.info(f"popup_version_control")
        popup = tk.Toplevel(self.main_frame)
        popup.title("Versioncontrol")
        popup.geometry("1200x800")
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_columnconfigure(0, weight=0)
        popup.grid_columnconfigure(1, weight=1)

        # OPTIONS FRAME (LEFT)
        options_frame = ctk.CTkFrame(popup, fg_color="lightgrey")
        options_frame.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")
        options_frame.rowconfigure((0,1,2,3), weight=0) # depends on number of lines with widgets
        options_frame.columnconfigure(0, weight=1)
        options_frame.columnconfigure(1, weight=0)

        # COMMIT/VERSION FRAME (INSIDE OPTIONS FRAME)
        version_frame = ctk.CTkFrame(options_frame, fg_color="lightgrey")
        version_frame.grid(row=4, column=0, columnspan=2, padx=(3,3), pady=(5,5), sticky="news")
        version_frame.rowconfigure(0, weight=1)
        version_frame.columnconfigure(0, weight=1)
        version_frame.columnconfigure(1, weight=0)
        
        # DIFF FRAME for displaying the changes (RIGHT)
        diff_frame = ctk.CTkFrame(popup, fg_color="lightgrey")
        diff_frame.grid(row=0, column=1, padx=3, pady=3, sticky="nsew")
        diff_frame.rowconfigure(0, weight=0)
        diff_frame.rowconfigure(1, weight=1)
        diff_frame.columnconfigure(0, weight=1)

        # LABELS for content frames 
        options_frame_label = ctk.CTkLabel(options_frame, text="Options", height=30, font=("default",14), text_color="black") 
        diff_frame_label = ctk.CTkLabel(diff_frame, text="Displayed Changes", height=30, font=("default",14), text_color="black")

        ###### WIDGETS ######
        # User input file to track changes of git 
        self.file_path_entry_label = ctk.CTkLabel(options_frame, text="File Path (to load the commit history):", font=("default", 12), text_color="black")
        self.file_path_entry = ctk.CTkEntry(options_frame, width=200, placeholder_text="Enter a file path for version control")
        # Create and configure Treeview style
        style = ttk.Style()
        style.configure("Treeview", foreground="black", background="white", font=("default", 10), fieldbackground="white") # , fieldbackground="white" #, foreground="black", background="white"
        style.configure("Treeview.Heading", foreground="black", background="white", font=("default", 10, "bold"))
        
        # Treeview for commit history
        self.version_tree = ttk.Treeview(
            version_frame,
            style="Custom.Treeview",
            columns=("Commit", "Message", "Date"), 
            show="headings", 
            height=20
        )
        self.version_tree.heading("Commit", text="Commit Hash")
        self.version_tree.heading("Message", text="Message")
        self.version_tree.heading("Date", text="Date")
        self.version_tree.column("Commit", width=120)
        self.version_tree.column("Message", width=250)
        self.version_tree.column("Date", width=150)
        # Add vertical scrollbar
        scrollbar = ttk.Scrollbar(version_frame, orient="vertical", command=self.version_tree.yview)
        self.version_tree.configure(yscroll=scrollbar.set)

        # NOTE: default path is the latest sysml model 
        diff_text_widget = tk.Text(diff_frame, wrap=tk.WORD)

        btn_show_version_history = ctk.CTkButton(options_frame, text="Show History", width=30, command=lambda: self.show_version_history(file_path=self.file_path_entry.get(), treeview_widget=self.version_tree))
        btn_load_diff = ctk.CTkButton(options_frame, text="See changes", width=100, command=lambda: self.show_version_diff(file_path=self.file_path_entry.get(), text_widget=diff_text_widget))
        
        ###### LAYOUT ######
        # OPTIONS FRAME LAYOUT (LEFT)
        options_frame_label.grid(row=0, column=0, columnspan=2, pady=2, sticky="ew")
        self.file_path_entry_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.file_path_entry.grid(row=2, column=0, padx=10, pady=(0,10), sticky="ew")
        self.version_tree.grid(row=0, column=0, padx=(10,0), pady=(0,10), sticky="news")
        scrollbar.grid(row=0, column=1, padx=(5,10), pady=(0,10), sticky="ns") 
        btn_show_version_history.grid(row=2, column=1, padx=(0,10), pady=(0,10), sticky="ew") 
        btn_load_diff.grid(row=5, column=0, columnspan=2, padx=(10,10), pady=(0,10), sticky="ew")
        # DIFF FRAME LAYOUT (RIGHT)
        diff_frame_label.grid(row=0, column=0, pady=2, sticky="ew")
        diff_text_widget.grid(row=1, column=0, padx=5, pady=5, sticky="news")
        
    def show_version_diff(self, file_path, text_widget):
        """
        Displays the differences/changes between the selected commits to the text widget (used in the diff_frame)
        
        Parameters:
            file_path : String. Contains relative path to the file to be searched with commit history
            text_widget: (tk) Text object. To be filled with content from git diff 
        Returns: 
            Updated (tk) Text widget with content (string format)
        """
        #self.logger.info(f"show_version_diff")
        # Clear current text widget 
        text_widget.delete("1.0", tk.END)

        # Check if file path is not empty
        if file_path == "":
            self.logger.error("No file path provided")
            text_widget.insert(tk.END, "No file path provided")
            messagebox.showwarning("Warning", f"No File Path provided. Please insert a file path.")
            return

        # Check if file path exists
        if not file_path: 
            self.logger.error("No file path provided")
            messagebox.showwarning("Warning", f"No File Path provided. Please insert a file path.")
            return

        # Get selected commit has from Treeview
        selected_item = self.version_tree.selection()
        if not selected_item: 
            self.logger.error("No commit selected")
            text_widget.insert(tk.END, "No commit selected. Please select inside the Options menu.")
            return

        # column 0 := hash; first treeview heading 
        selected_commit_hash = self.version_tree.item(selected_item, "values")[0]
        self.logger.debug(f"User selected commit with hash: {selected_commit_hash}")
        # Call Versioncontrol function to get the git diff 
        diff = self.vc.get_diff_with_specific_commit(file_path=file_path, commit_hash=selected_commit_hash)
        if not diff: 
            text_widget.insert(tk.END, "No differences found")

        # Parse and display diff with colors
        for line in diff.splitlines():
            if line.startswith("diff --git") or line.startswith("index") or line.startswith("---") or line.startswith("+++"):
                continue  # Skip unnecessary lines
            elif line.startswith("@@"):
                text_widget.insert(tk.END, f"{line}\n", "header")
            elif line.startswith("+"):
                text_widget.insert(tk.END, f"{line}\n", "added")
            elif line.startswith("-"):
                text_widget.insert(tk.END, f"{line}\n", "removed")
            else:
                text_widget.insert(tk.END, f"{line}\n", "normal")

        # Apply color tags 
        text_widget.tag_configure("added", background="green") #foreground 
        text_widget.tag_configure("removed", background="red")
        text_widget.tag_configure("header", background="blue", font=("default", 12, "bold"))
        text_widget.tag_configure("normal", background="white") #background="black"
        text_widget.tag_configure("error", background="red", font=("default", 12, "italic"))
        text_widget.tag_configure("info", background="blue", font=("default", 12, "italic"))

    def show_version_history(self, file_path, treeview_widget): 
        """Displays the commit history for user selection (used for popup_version_control)
            inside the treeview widget
        """
        #self.logger.info(f"show_version_history")
        
        file_path = filedialog.askopenfilename(title="Select a file for version control", filetypes=[("All files", "*.*"), ("SysML files", "*.sysml")])
        if not file_path: 
            self.logger.error("No file path provided")
            messagebox.showwarning("Warning", f"No File Path provided. Please insert a file path.")
            return

        self.file_path_entry.delete(0, tk.END)
        self.file_path_entry.insert(0, file_path)

        # Empty treeview before adding elements 
        for row in treeview_widget.get_children():
            treeview_widget.delete(row)
        #self.logger.debug(f"Treeview widget cleared")

        self.vc.load_commit_history_from_file_path(file_path=file_path, treeview_widget=treeview_widget)

    def popup_verification(self):
        """
        Opens a popup to verify constraints inside the SysMLv2 Model
        NOTE: For demonstration the sysml model is setup to contain mass constraint 

        1) User selects sysml model to verify 
        2) GUI parses through and returns all constraints inside sysml model
        3) User selects which constraint he wants to check 
        4) Program transforms textual notation into real mathematical equation to perfom constraint check
        5) Shows user if selected constraint is checked or not 
        """
        # self.logger.info(f"popup_verification)
        popup = tk.Toplevel(self.main_frame)
        popup.title("Verification Analysis")
        popup.geometry("1500x1000")
        popup.grid_rowconfigure(0, weight=1)
        popup.grid_rowconfigure(1, weight=1)
        popup.grid_columnconfigure(0, weight=1) # to "span" frames to whole popup

        ########## FRAMES ##########
        # SYSML FRAME: Upper
        sysml_frame = ctk.CTkFrame(popup, fg_color="lightgrey")
        sysml_frame.rowconfigure(0, weight=0) # Used for label with set custom height 
        sysml_frame.rowconfigure(1, weight=1)
        sysml_frame.columnconfigure(1, weight=1)
        sysml_frame.columnconfigure(0, weight=1)
        # VERIFICATION FRAME: Lower
        verification_frame = ctk.CTkFrame(popup, fg_color="lightgrey") #lightgrey
        verification_frame.rowconfigure(0, weight=1) # Used for label with set custom height 
        verification_frame.rowconfigure(1, weight=1)
        verification_frame.columnconfigure(0, weight=1)
        verification_frame.columnconfigure(1, weight=0)

        # POPUP LAYOUT 
        sysml_frame.grid(row=0, column=0, padx=3, pady=3, sticky="nsew") 
        verification_frame.grid(row=1, column=0, padx=3, pady=3, sticky="nsew") 


        ########## WIDGETS ########## 
        sysml_frame_label = ctk.CTkLabel(sysml_frame, text="SysMLv2", height=30, font=("default",14), text_color="black") 
        sysml_frame_text_widget = tk.Text(sysml_frame, wrap=tk.WORD)
        btn_load_model_sysml = ctk.CTkButton(sysml_frame, text="Load SysML Model", command=lambda: self.select_file(model_type="sysml", text_widget=sysml_frame_text_widget))

        verification_frame_label = ctk.CTkLabel(verification_frame, text="Verification Analysis", height=30, font=("default",14), text_color="black") 
        verification_frame_constraint_label = ctk.CTkLabel(verification_frame, text="Constraint Name", font=("default",12), text_color="black")
        verification_frame_constraint_entry = ctk.CTkEntry(verification_frame, placeholder_text="Type the constraint name to verify")
        btn_verify_constraint = ctk.CTkButton(verification_frame, text="Verify", command=lambda: self.verify_selected_constraint(verification_frame_constraint_entry.get()))
        ########## LAYOUT ##########
        # SYSML FRAME LAYOUT 
        sysml_frame_label.grid(row=0, column=0, padx=5, pady=(5,0), sticky="news") 
        sysml_frame_text_widget.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew") 
        btn_load_model_sysml.grid(row=0, column=1, padx=5, pady=(5,0), sticky="e")

        verification_frame_label.grid(row=0, column=0, padx=5, pady=(5,0), sticky="news") 
        verification_frame_constraint_label.grid(row=1, column=0, padx=5, sticky="w")
        verification_frame_constraint_entry.grid(row=2, column=0, padx=5, sticky="ew")
        btn_verify_constraint.grid(row=2, column=1, padx=5, pady=(5,0), sticky="ew")
    
    def verify_selected_constraint(self, constraint_name): 
        """
        Verify user selected constraint (from constraint_entry)
        """
        # Load sysml model 
        # NOTE: By using select_file the file path already sets the sysml model path that the user selected
        if self.sysml_model: 
            # Load function from SysmlParser Class (file_parser) to parse and check constraint 
            self.sysml_model.verify_constraint()
        else:
            self.logger.error(f"Could not verify constraint: {constraint_name}")
            raise ValueError(f"Could not verify constraint: {constraint_name}")

def main(): 
    # Run Initial Log Setup for debugging
    setup_logging() 
    # Load Default Config File from config folder   
    DEFAULT_CONFIG_FILE = "config/default_config.json" 
    DEFAULT_CONFIG = load_config(DEFAULT_CONFIG_FILE)

    # Create Parser object classes for functions that can read, parse and edit these specific files
    fp_sysml = SysmlParser(sysml_path="models/se_domain/example_drone_origin.sysml")
    fp_code = CodeParser(code_file_path = "models/sw_domain/generated_code.py")
    fp_gerber = GerberParser(gerber_file_path="models/ee_domain/Hades_project-job.gbrjob")
    fp_step = StepParser(step_file_path="models/me_domain/STEP_AgriUAV.stp")
    vc = VersionControl(config=DEFAULT_CONFIG)
    mm = MetadataManager(config=DEFAULT_CONFIG, versioncontrol=vc, gerberparser=fp_gerber, stepparser=fp_step, codeparser=fp_code, sysmlparser=fp_sysml) 
    
    mm.update_sysml_model()

    #metadata = fp_sysml.get_metadata_about_elements()
    #print(metadata)
    generated_code = fp_code.generate_code_from_sysml(sysml_file_path="models/se_domain/example_drone_origin.sysml")
    

    # TESTING CODE GENERATION
    # fp_code = CodeParser()
    # python_code = fp_code.generate_code()
    # print(f"Generated Python Code: {python_code}")
    # fp_code.save_code(code=python_code, filename="generated_code.py")

    # Start the Tkinter app
    app = GUI(config=DEFAULT_CONFIG, metadatamanager=mm, versioncontrol=vc)
    app.root.mainloop() 

if __name__ == "__main__":
    main() 
