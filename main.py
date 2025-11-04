import os
import logging
import sys # Used for installing requirements and checking docker 
import subprocess # Used for SysON visualization and loading Docker-Compose file; used to run external commands

def check_virtualenv():
    """ Check if we are in a virtual environment or a Conda environment """
    logger = logging.getLogger(__name__)
    
    # Prüfe, ob eine venv aktiv ist
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

    # Prüfe, ob eine Conda-Umgebung aktiv ist
    in_conda = os.environ.get("CONDA_PREFIX") is not None

    if in_venv:
        logger.info("Virtual environment (venv) is active.")
    elif in_conda:
        logger.info("Conda environment is active.")
    else:
        logger.error(
            "You are not in a virtual environment or a Conda environment.\n"
            "To create a venv, run: 'python -m venv your_env_name'\n"
            "To activate (Windows): 'your_env_name\\Scripts\\activate'\n"
            "To activate (Linux/macOS): 'source your_env_name/bin/activate'\n"
            "To create a Conda env, run: 'conda create --name your_env_name python=3.x'\n"
            "To activate Conda env: 'conda activate your_env_name'"
        )
        sys.exit(1)

def install_requirements():
    """Install dependencies from requirements.txt if they are not already installed."""
    if not os.path.exists('requirements.txt'):
        print("Error: The requirements.txt file was not found!")
        sys.exit(1)

    try:
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    except Exception as e:
        print(f"Something went wrong during installation of requirements: {e}")
        sys.exit(1)


# Check 
check_virtualenv()
# Check Requirements     
install_requirements() 


import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import StringVar # used for Dropdown menus 
from tkinter import filedialog # used for loading files via file explorer of the OS 
import customtkinter as ctk
import threading # Used for parellized tasks (running docker file); used for threading DURING program execution
import webbrowser #webview # Used for SysON visualization. To install use pip install pywebview

# Utils and module references
from file_parser import GerberParser
from file_parser import SysmlParser
from file_parser import StepParser
from file_parser import CodeParser
from AUTOSAR_Parser import AUTOSAR_Parser

from utils.config_utils import save_config, load_config
from metadata_manager import MetadataManager
from versioncontrol import VersionControl 


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

def check_docker():
    """ Check if Docker is installed and running """
    logger = logging.getLogger(__name__)
    logger.info("Checking if Docker is installed on the system.")
    try:
        logger.info("Checking Docker version...")
        result = subprocess.run(["docker", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            logger.info(f"Docker is installed: {result.stdout.strip()}")
        else:
            logger.error("Docker is not running or installed. Please install and/or run Docker Desktop.")
            sys.exit(1)
    except FileNotFoundError:
        logger.error("Docker command not found. Is it installed?")
        sys.exit(1)
    
class DockerManager:
    """Executing and managing Docker files"""
    def __init__(self):
        super().__init__() 
        self.logger = logging.getLogger(__name__)
        #self.logger.info(f"Initialized DockerManager")
        self.compose_file_path = "./docker_master/docker-compose-master.yml"

        #self.start_docker_services()

    def start_docker_services(self): 
        """Starts the docker compose services"""
        self.logger.info(f"start_docker_services")
        # Helper Function
        def run_compose_file(): 
            try: # --build to build with latest build instructions from docker compose file
                subprocess.run(["docker-compose", "-f", self.compose_file_path, "up", "--build", "-d"], check=True) # docker compose -f docker-compose-master.yml --build 
                self.logger.info("Docker Compose started successfully")
            except FileNotFoundError:
                self.logger.error("docker-compose not found. Please install Docker.")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Error while starting Docker Compose: {e}")

        # daemon threads are closed automatically when main program is closed and avoid blocking the main program
        self.logger.debug("Running docker compose file in a new thread")
        threading.Thread(target=run_compose_file, daemon=True).start()

class GUI:
    """
    Main application for the GUI, managing user interaction.
    Uses Tkinter for the user interface.
    """
    def __init__(self, config, metadatamanager=None, versioncontrol=None): 
        self.logger = logging.getLogger(__name__ + "-GUI")
       
        self.config = config
        # List acts as the accepted file formats (used inside the map popup)
        self.available_file_formats = ["GerberJobFile", "STEP", "Source Code","AUTOSAR"]
        # List for available datatypes and si units
        self.available_datatypes = ["int", "float", "string", "bool"]
        self.available_units = ["", "m", "cm", "mm", "kg", "s", "A", "K", "mol", "m^2", "m^3", "N", "Pa", "J", "W", "C", "V", "F"]

        self.sysml_model = None #initialized object from sysml parser of file_parser sysml_parser
        self.sysml_file_path = ""
        self.domain_file_path = ""

        self.mm = metadatamanager
        self.vc = versioncontrol

        # SysON Webview
        self.syson_url = "http://localhost:8081/projects"

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
        #self.select_sysml_model = ctk.CTkButton(self.main_frame, text="Select SysML Model", command=self.select_sysml_model)
        self.btn_visualize_sysml_model = ctk.CTkButton(self.main_frame, text="Visualize SysML Model", command=self.popup_syson)
        self.btn_edit_sysml_model = ctk.CTkButton(self.main_frame, text="View/Edit SysML Model", command=self.popup_edit_sysml_model)
        self.btn_map_data = ctk.CTkButton(self.main_frame, text="Map Data", command=self.popup_map_data)  
        self.btn_version_control = ctk.CTkButton(self.main_frame, text="Version Control", command=self.popup_version_control)
        self.btn_verification = ctk.CTkButton(self.main_frame, text="Verification Analysis", command=self.popup_verification)
        self.btn_consistency_manager = ctk.CTkButton(self.main_frame, text="Update Consistency", command=lambda: self.mm.update_sysml_model())
        self.btn_mapping_editor = ctk.CTkButton(self.main_frame, text="Edit Mappings", command=self.popup_mapping_editor)
        self.btn_change_log = ctk.CTkButton(self.main_frame, text="View Value Changes", command=self.popup_change_log)
        

    def setup_layout(self):
        """Sets up the layout of the GUI elements."""
        #self.logger.info(f"setup_layout")
        self.main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.root.grid_rowconfigure(0, weight=1)  
        self.root.grid_columnconfigure(0, weight=1) 
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure((0,1,2,3,4,5), weight=0)

        #self.select_sysml_model.grid(row=0, column=0, padx=5, pady=(10,5), sticky="ew")
        self.btn_visualize_sysml_model.grid(row=1, column=0, padx=5, pady=(10,5), sticky="ew")
        self.btn_edit_sysml_model.grid(row=8, column=0, padx=5, pady=(10,5), sticky="ew")
        self.btn_map_data.grid(row=2, column=0, padx=5, pady=5, sticky="ew") 
        self.btn_version_control.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        self.btn_verification.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
        self.btn_consistency_manager.grid(row=5, column=0, padx=5, pady=5, sticky="ew")
        self.btn_mapping_editor.grid(row=6, column=0, padx=5, pady=5, sticky="ew")
        self.btn_change_log.grid(row=7, column=0, padx=5, pady=5, sticky="ew")


    def popup_syson(self):
        """
        NOTE: OPTIONAL "PLUGIN" TO VISUALIZE THE SYSML MODEL IN A WEB INTERFACE
        Opens the SysON web interface inside the popup window of the GUI
        Uses: webview (pywebview) library
        """
        # webview.create_window("SysON Model Visualization", url=self.syson_url, width=1600, height=1200, resizable=True)
        # webview.start()
        webbrowser.open(self.syson_url)
        
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
        popup.grid_columnconfigure(0, weight=1)
        popup.grid_columnconfigure(1, weight=1)

        ########## FRAMES ##########
        # SYSML FRAME: LEFT
        sysml_frame = ctk.CTkFrame(popup, fg_color="lightgrey")
        sysml_frame.rowconfigure(0, weight=0)
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
        selected_domain_element_name = StringVar(value="Enter a domain element path e.g. 'GeneralSpecs.Size.X'")
        selected_domain_element_value = StringVar(value="Enter integer Number e.g. '7.42'")
        selected_domain_element_write_prio = StringVar(value=f"Enter Number (smaller than {self.mm.default_sysml_element_write_prio} = read only from sysml and write only to smaller values)")
        sysml_frame_label = ctk.CTkLabel(sysml_frame, text="SysMLv2 File", height=30, font=("default",14), text_color="black") 
        domain_frame_label = ctk.CTkLabel(domain_frame, text="Domain File", height=30, font=("default",14), text_color="black")
        map_frame_label = ctk.CTkLabel(map_frame, text="Map Elements", height=30, font=("default", 14), text_color="black")

        sysml_frame_text_widget = tk.Text(sysml_frame, wrap=tk.WORD)
        btn_load_model_sysml = ctk.CTkButton(sysml_frame, text="Load SysML Model", command=lambda: self.select_file(model_type="sysml", text_widget=sysml_frame_text_widget))
        
        selected_domain_format = StringVar(value=self.available_file_formats[0]) #[0] first element is the default value
        domain_file_format_dropdown = ctk.CTkOptionMenu(domain_frame, values=self.available_file_formats,variable=selected_domain_format)
        domain_frame_content_frame = ctk.CTkFrame(domain_frame, fg_color="lightgrey")
        domain_frame_content_frame.rowconfigure(0,weight=1)
        domain_frame_content_frame.columnconfigure(0,weight=1)
        btn_load_model_domain = ctk.CTkButton(domain_frame, text="Load Domain Model", 
                                             command=lambda: self.select_file(model_type="domain", content_frame=domain_frame_content_frame, selected_domain_element_name=selected_domain_element_name, selected_domain_element_value=selected_domain_element_value))
        # MAP FRAME:        Labels, Entries and Button for user input to connect elements
        map_frame_sysml_name_label = ctk.CTkLabel(map_frame, text="SysML Element Path:", font=("default", 12), text_color="black")
        map_frame_sysml_name_entry = ctk.CTkEntry(map_frame, placeholder_text="Enter a sysml element path e.g 'package.partA.len'")
        map_frame_sysml_value_label = ctk.CTkLabel(map_frame, text="SysML Element Value:",font=("default", 12), text_color="black")
        map_frame_sysml_value_entry = ctk.CTkEntry(map_frame, placeholder_text="Enter corresponding element value e.g. 50")
        selected_sysml_element_unit = StringVar(value=self.available_units[0]) # initial value
        map_frame_sysml_unit_dropdown = ctk.CTkOptionMenu(map_frame, values=self.available_units,variable=selected_sysml_element_unit)
        map_frame_sysml_unit_dropdown_label = ctk.CTkLabel(map_frame, text="SysML Element Unit (if possible):",font=("default", 12), text_color="black")
        
        map_frame_domain_name_label = ctk.CTkLabel(map_frame, text="Domain Element Path:", font=("default", 12), text_color="black")
        map_frame_domain_name_entry = ctk.CTkEntry(map_frame, placeholder_text="Enter a domain element path e.g. 'GeneralSpecs.Size.X'",textvariable=selected_domain_element_name)
        map_frame_domain_value_label = ctk.CTkLabel(map_frame, text="Domain Element Value:", font=("default", 12), text_color="black") 
        map_frame_domain_write_prio_entry = ctk.CTkEntry(map_frame, placeholder_text=f"Enter Number (smaller than {self.mm.default_sysml_element_write_prio} = read only from sysml and write only to smaller values)",textvariable=selected_domain_element_write_prio)
        map_frame_domain_write_prio_label = ctk.CTkLabel(map_frame,text="write_prio:",font=("default", 12), text_color="black",justify="right",anchor="w")
        map_frame_domain_value_entry = ctk.CTkEntry(map_frame, placeholder_text="Enter integer Number e.g. '7.42'",textvariable=selected_domain_element_value)
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
                                                                   selected_domain_element_name, 
                                                                   selected_domain_element_value,
                                                                   selected_domain_element_unit,
                                                                   selected_domain_element_write_prio))

        ########## LAYOUT ##########
        # SYSML FRAME LAYOUT 
        sysml_frame_label.grid(row=0, column=0, padx=5, pady=(5,0), sticky="news") 
        sysml_frame_text_widget.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew") 
        btn_load_model_sysml.grid(row=0, column=1, padx=5, pady=(5,0), sticky="e") 
        # DOMAIN FRAME LAYOUT 
        domain_frame_label.grid(row=0, column=0, pady=(5,0), sticky="ew")
        domain_frame_content_frame.grid(row=1, column=0,columnspan=3, padx=5, pady=5, sticky="nsew")
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
        map_frame_domain_write_prio_label.grid(row=7, column=1, columnspan=1, padx=(5,10), pady=(2,5), sticky="e")
        map_frame_domain_write_prio_entry.grid(row=7, column=2, columnspan=2, padx=(5,10), pady=(2,5), sticky="ew")
        


        btn_map_elements.grid(row=8, column=1, columnspan=2, padx=(5,5), pady=(10,10), sticky="ew")

    def select_sysml_model(self):
        """
        Opens a file dialog to select a SysML file. 
        """
        file_path = filedialog.askopenfilename(title="Select SysML File", filetypes=[("SysML Files", "*.sysml"), ("All Files", "*.*")])

        if file_path: 
            self.sysml_file_path = file_path

    def select_file(self, model_type, content_frame=None, selected_domain_element_name=None, selected_domain_element_value=None, text_widget=None):
        """ 
        Opens a file dialog to select a SysML file inside the file explorer of the OS 
        """ 
        self.logger.info("[GUI:select_file()]: attemting to select File")

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
            self.logger.info(f"[GUI:select_file()]: File selection successful with file {filepath}. Proceeding to load file by function call of GUI:load_file_content()")        
            self.load_file_content(file_path=filepath, content_frame=content_frame, selected_domain_element_name=selected_domain_element_name, selected_domain_element_value=selected_domain_element_value, text_widget=text_widget)
            
    def load_file_content(self, file_path, content_frame=None, selected_domain_element_name=None, selected_domain_element_value=None, text_widget=None):
        """Loads file content into the given text widget."""
        self.logger.info(f"[GUI:load_file_content()]: attemting to load file content of file {file_path}")
        if text_widget != None:
            self.logger.info(f"[GUI:load_file_content()]: trying to directly load file content into text_widget")
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    text_widget.config(state=tk.NORMAL)  # Set text widget to normal and paste the content
                    text_widget.delete("1.0", tk.END)  # Clear previous text 
                    text_widget.insert(tk.END, content)  # Write new content to text widget 
                    text_widget.config(state=tk.DISABLED)  # Set text widget to read only 
                self.logger.info(f"[GUI:load_file_content()]: content was loaded to text_widget successfully")
                return content 
            except Exception as e:
                self.logger.error(f"[GUI:load_file_content()]: Failed to load file {file_path}: {e}")
                text_widget.delete("1.0", tk.END)  # Clear previous text 
                text_widget.insert(tk.END, f"Error loading file: {e}")  
                return False

        # Clear Frame
        if content_frame == None:
            self.logger.error("[GUI:load_file_content()]: no content_frame provided to load data into")
            return False
        self.logger.info(f"[GUI:load_file_content()]:clearing content_frame")
        for widget in content_frame.winfo_children():
            self.logger.info(f"[GUI:load_file_content()]:     destroying widget {widget}")
            widget.destroy()

        if file_path.split(".")[-1] == "arxml":

            if selected_domain_element_name == None or  selected_domain_element_value== None:
                self.logger.error("[GUI:load_file_content()]: no content_frame and/or Stringvars provided")
                return False
            self.logger.info(f"[GUI:load_file_content()]: trying to load file content into treeView as ist is an .arxml file")
            tv=self.generate_treeView_from_arxml(content_frame,AUTOSAR_Parser(AUTOSAR_file_path=file_path),selected_domain_element_name,selected_domain_element_value)
            self.logger.info(f"[GUI:load_file_content()]: treeView loaded successfully with content")
            return True

        self.logger.info(f"[GUI:load_file_content()]: trying to load file content into text_widget inside a content_frame")
        text_widget = tk.Text(content_frame, wrap=tk.WORD)
        text_widget.grid(row=0, column=0, sticky="nsew")
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                text_widget.config(state=tk.NORMAL)  # Set text widget to normal and paste the content
                text_widget.delete("1.0", tk.END)  # Clear previous text 
                text_widget.insert(tk.END, content)  # Write new content to text widget 
                text_widget.config(state=tk.DISABLED)  # Set text widget to read only 
                self.logger.info(f"[GUI:load_file_content()]: successfully loaded file content into text_widget inside content_frame")
            return content 
        
        except Exception as e:
            self.logger.error(f"[GUI:load_file_content()]: Failed to load file {file_path}: {e}")
            text_widget.delete("1.0", tk.END)  # Clear previous text 
            text_widget.insert(tk.END, f"Error loading file: {e}")  
            return False

    def map_elements(self, sysml_path, sysml_element_path, sysml_element_value, sysml_element_unit, 
                     domain_file_format, domain_path, domain_element_path, domain_element_value, domain_element_unit, domain_element_write_prio): 
        """
        - metadata_manager has to parse file via file_parser functions to get specific user given path 
        to the element in order to generate UUID and map correctly 
        
        """
        #self.logger.info(f"map_elements")
        #self.logger.debug(f"User provided sysml path inside entry: {sysml_path}")
        sysml_element_path = sysml_element_path.get()
        sysml_element_value = sysml_element_value.get()
        sysml_element_unit = sysml_element_unit.get()
        domain_file_format = domain_file_format.get() 
        domain_element_path = domain_element_path.get()
        domain_element_value = domain_element_value.get()
        domain_element_unit = domain_element_unit.get()
        domain_element_write_prio = domain_element_write_prio.get()
        #Initialize SysmlParser analog to 'popup_edit_sysml_model'
        self.sysml_model = SysmlParser(sysml_path=sysml_path) 
        #self.logger.debug(f"Created SysML Parser instance: {self.sysml_model}")
        # Validate user given element path (function from file parser)
        if not self.sysml_model.validate_elementPath(elementPath=sysml_element_path): 
            self.logger.warning(f"User provided an invalid sysml element pathing: {sysml_element_path}")
            messagebox.showerror("ERROR", "Provided SysML element path is invalid.")
        
        else:
            self.logger.info(f"VALIDATION: SysMLv2 elementpath: {sysml_element_path}, VALID: True")
            if self.mm.map_metadata(sysml_path, sysml_element_path, sysml_element_value, sysml_element_unit, 
                                    domain_file_format, domain_path, domain_element_path, domain_element_value, 
                                    domain_element_unit, domain_element_write_prio):
                # Notify the user about the successful mapping
                messagebox.showinfo("INFO", "Successfully mapped elements together!")

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
        verification_frame.rowconfigure(0, weight=0) # Used for label with set custom height 
        verification_frame.rowconfigure((1,2), weight=0)
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
        verification_frame_constraint_label = ctk.CTkLabel(verification_frame, text="Constraint Name (Usage)", font=("default",12), text_color="black")
        verification_frame_constraint_entry = ctk.CTkEntry(verification_frame, placeholder_text="Type the constraint name to verify e.g. ")
        btn_verify_constraint = ctk.CTkButton(verification_frame, text="Verify", command=lambda: self.verify_selected_constraint(verification_frame_constraint_entry.get()))
        ########## LAYOUT ##########
        # SYSML FRAME LAYOUT 
        sysml_frame_label.grid(row=0, column=0, padx=5, pady=(5,0), sticky="news") 
        sysml_frame_text_widget.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="nsew") 
        btn_load_model_sysml.grid(row=0, column=1, padx=5, pady=(5,0), sticky="e")

        verification_frame_label.grid(row=0, column=0, padx=5, pady=(5,0), sticky="news") 
        verification_frame_constraint_label.grid(row=1, column=0, padx=5, pady=(5,0), sticky="w")
        verification_frame_constraint_entry.grid(row=2, column=0, padx=5, pady=(3,0), sticky="ew")
        btn_verify_constraint.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
    
    def verify_selected_constraint(self, constraint_name): 
        """
        Verify user selected constraint (from constraint_entry)
        """
        #self.logger.info(f"verify_selected_constraint")
        # Load sysml model 
        # NOTE: By using select_file the file path already sets the sysml model path that the user selected
        self.logger.debug(f"Current sysml file path: {self.sysml_file_path}")
        self.sysml_model = SysmlParser(sysml_path=self.sysml_file_path)

        if self.sysml_model: 
            # Load function from SysmlParser Class (file_parser) to parse and check constraint 
            response = self.sysml_model.verify_constraint(self.sysml_file_path, constraint_name)

            def custom_messagebox(title, message):
                popup = tk.Toplevel()
                popup.title(title)
                popup.geometry("500x100")

                text_color = "green" if "(TRUE)" else "red"
                label = tk.Label(popup, text=message, font=("Arial", 12, "bold"), fg=text_color)
                label.pack(pady=20)

                popup.transient()  # stays in the foreground
                popup.grab_set()  # prevents interaction with main window

            custom_messagebox("INFO", response)

        else:
            self.logger.error(f"Could not verify constraint: {constraint_name}")
            raise ValueError(f"Could not verify constraint: {constraint_name}")
        

    def generate_treeView_from_arxml(self, content_frame, AUTOSAR_Parser, selected_domain_element_name, selected_domain_element_value):
        """
        Generate TreeView Object that corresponds to the provided arxml file in the parser and add it to provided content_frame
        :param content_frame: ctk Frame to which the Treeview will be bound
        :param AUTOSAR_Parser: Parser for arxml-files
        :param selected_domain_element_name: Stringvar that holds elementPath to Domain element. Shall be changed when selection event occurs
        :param selected_domain_element_value: Stringvar that holds value that will be displayed and mapped in mapping Tool
        :return: TreeView Object or None if Error
        """
        self.logger.info(f"[GUI:generate_treeView_from_arxml()]: attemting to generate TreeView Object from arxml file")
        param_is_invalid = 0
        if not content_frame: param_is_invalid  = 1
        if not AUTOSAR_Parser: param_is_invalid = 2
        if selected_domain_element_name == None or not isinstance(selected_domain_element_name,StringVar): param_is_invalid = 3
        if selected_domain_element_value == None or not isinstance(selected_domain_element_value,StringVar): param_is_invalid = 4
        if param_is_invalid > 0:
            self.logger.error(f"[GUI:generate_treeView_from_arxml()]: At least Parameter {param_is_invalid} is invalid")
            return None
        self.logger.info(f"[GUI:generate_treeView_from_arxml()]: input parameters are valid. Proceeding to generate TreeView from file {AUTOSAR_Parser.file_path}")
        
        #get arxml Tree Object and TreeView Object
        tv = ttk.Treeview(content_frame,show="tree", selectmode="browse",height=30)
        tv.bind("<<TreeviewSelect>>", lambda event: self.set_map_frame_domain_value_entry(event, tv, selected_domain_element_name,selected_domain_element_value))
        AUTOSAR_Parser.load_file()
        arxml_root = AUTOSAR_Parser.tree_root
        
        if arxml_root == None:
            self.logger.error("[GUI:generate_treeView_from_arxml()]: arxml-file could not be loaded or elementTree could not be instantiated")
            return None
        tv.column("#0",stretch=False,width=950)
        
        tv_root = tv.insert("", tk.END, text=self.generate_tv_element_full_name(arxml_root))

        #iterate over arxml-tree amd add corresponding elements to Treeview
        self.logger.info(f"[GUI:generate_treeView_from_arxml()]: Tree root generated. Proceeding to recursively populate Tree")

        self.rec_generate_treeView_from_arxml(arxml_root, tv_root, tv)
        
        tv.grid(row=0,column=0,sticky="nsew")
        self.logger.info(f"[GUI:generate_treeView_from_arxml()]: Successfully generated TreeView")
        return tv

    def rec_generate_treeView_from_arxml(self, arxml_parent, tv_parent, tv):
        """
        Add children to tv_parent consistent with arxml_parents children
        :param arxml_parent: arxml elementTree Object corresponding to tv_parent
        :param tv_parent: TreeView item Object to which the children shall be added to
        :param tv: TreeView Object
        :return: Nothing
        """
        self.logger.info(f"[GUI:rec_generate_treeView_from_arxml()]: attemting to add childs to parent {arxml_parent.tag}")
        for arxml_child in arxml_parent.findall("./*"):
            tv_element_full_name = self.generate_tv_element_full_name(arxml_child)
            tv_child = tv.insert(tv_parent, tk.END, text=tv_element_full_name)
            self.logger.info(f"[GUI:rec_generate_treeView_from_arxml()]:     inserting child {arxml_child.tag} to {arxml_parent.tag}")
            self.rec_generate_treeView_from_arxml(arxml_child, tv_child, tv)

    def generate_tv_element_full_name(self, arxml_element):
        """
        get Text that shall be displayed for the arxml_element in the generated treeView
        :param arxml_element: element in elementTree Object
        :return: String of Format (SHORT-NAME)<TAG ATTRIBUTES>TEXTVALUE</TAG>
        """
        self.logger.info(f"[GUI:generate_tv_element_full_name()]: attemting to generate tv_full name from arxml element")
        
        if arxml_element == None:
            self.logger.error("[GUI:generate_tv_element_full_name()]: arxml_element is None")
            return None
        self.logger.info(f"[GUI:generate_tv_element_full_name()]: input parameters are valid. Proceeding to full_name generation")
        full_name = ""
        schema = arxml_element.tag.split("}")[0]+"}"
        # Add SHORT-NAME, if exists
        short_name_elem = arxml_element.find(f"./{schema}SHORT-NAME")
        if short_name_elem != None:
            full_name += "(" + short_name_elem.text + ")"

        #Add Tag
        full_name += "<"+arxml_element.tag.split("}")[-1]
        #add attributes to name, if exists
        attributes = arxml_element.items()  # returns sequence of (name,value) of all attributes of arxml_element
        if len(attributes) > 0:
            full_name += " "
            for (name, value) in attributes[:-1]:
                full_name += name+"="+value+","
            (name, value) = attributes[-1]
            full_name += name+"="+value
        full_name += ">"

        #add text value, is exists
        if arxml_element.text != None and arxml_element.text.strip() != "":
            full_name += arxml_element.text.strip(" \n")+"</"+arxml_element.tag.split("}")[-1]+">"

        self.logger.info(f"[GUI:generate_tv_element_full_name()]: Full Name generated successfully: {full_name}")
        return full_name

    def get_tv_text_value(self, tv_element_full_name):
        """
        return xml text value encoded in tv_element_full_name
        :param tv_element_full_name: String that is displayed in a treeView item Object; Format (SHORT-NAME)<TAG ATTRIBUTES>TEXTVALUE</TAG>
        :return: String xml text value (TEXTVALUE) that is encoded in tv_element_full_name
        """
        self.logger.info(f"[GUI:get_tv_text_value()]: attemting to get text value from full name: {tv_element_full_name}")
        if tv_element_full_name == None or tv_element_full_name == "" or tv_element_full_name.count(">") < 1:
            self.logger.error("[GUI:get_tv_text_value()]: tv_element_full_name is invalid")
            return None
        self.logger.info(f"[GUI:get_tv_text_value()]: input paramerters are valid. Proceeding to value generation")
        text_value = tv_element_full_name.split(">")[1]  #-> TEXT</TAG> oder ""
        text_value = text_value.split("<")[0]
        if text_value != "" and text_value != None and text_value != tv_element_full_name:
            self.logger.info(f"[GUI:get_tv_text_value()]: Value generation successful: {text_value}")
            return text_value
        self.logger.error(f"[GUI:get_tv_text_value()]: Value generation failed: {text_value} -> returning None")
        return None

    def get_tv_tag_value(self, tv_element_full_name):
        """
        return xml tag encoded in tv_element_full_name
        :param tv_element_full_name: String that is displayed in a treeView item Object; Format (SHORT-NAME)<TAG ATTRIBUTES>TEXTVALUE</TAG>
        :return: String xml Tag (TAG) that is encoded in tv_element_full_name
        """
        self.logger.info(f"[GUI:get_tv_tag_value()]: attemting to get tag value from full name: {tv_element_full_name}")
        if tv_element_full_name == None or tv_element_full_name == "" or tv_element_full_name.count(">") < 1:
            self.logger.error("[GUI:get_tv_tag_value()]: tv_element_full_name is empty")
            return None
        self.logger.info(f"[GUI:get_tv_tag_value()]: input paramerters are valid. Proceeding to value generation")
        tag_value = tv_element_full_name.split(">")[0]  #-> (SHORT-Name)<TAG ATTRIB
        tag_value = tag_value.split("<")[1]  # -> TAG ATTRIB
        tag_value = tag_value.split(" ")[0]  # -> TAG
        if tag_value != "" and tag_value != None:
            self.logger.info(f"[GUI:get_tv_tag_value()]: Value generation successful: {tag_value}")
            return tag_value
        self.logger.error(f"[GUI:get_tv_tag_value()]: Value generation failed: {tag_value} -> returning None")
        return None

    def get_tv_AUTOSAR_path_value(self, tv_element_full_name):
        """
        return AUTOSAR path value encoded in tv_element_full_name to get relative paths to the tv_item
        :param tv_element_full_name: String that is displayed in a treeView item Object; Format (SHORT-NAME)<TAG ATTRIBUTES>TEXTVALUE</TAG>
        :return: String AUTOSAR path value (SHORT-NAME) that is encoded in tv_element_full_name
        """
        self.logger.info(f"[GUI:get_tv_AUTOSAR_path_value()]: attemting to get AUTOSAR Path value from full name: {tv_element_full_name}")
        if tv_element_full_name == None or tv_element_full_name == "":
            self.logger.error("[GUI:get_tv_AUTOSAR_path_value()]: tv_element_full_name is empty")
            return None
        self.logger.info(f"[GUI:get_tv_AUTOSAR_path_value()]: input paramerters are valid. Proceeding to value generation")
        #check if tv_element_full_name has a AUTOSAR path value
        if tv_element_full_name[0] != "(":
            return None
        path_value = tv_element_full_name[1:].split(")")[0]
        if path_value != "" and path_value != None:
            self.logger.info(f"[GUI:get_tv_AUTOSAR_path_value()]: Value generation successful: {path_value}")
            return path_value
        self.logger.error(f"[GUI:get_tv_AUTOSAR_path_value()]: Value generation failed: {path_value} -> returning None")
        return None

    def get_tv_elementPath(self, tv, tv_item):
        """
        get elementPath to address tv_item in elementTree Object
        :param tv: TreeView Object
        :param tv_item: TreeVies item in tv to which the elementPath shall be generated
        :return: elementPath to tv_item; Format: Short-Names_of_elements_along_the_path.tag_names to item after last short name.tag_of_tv_item (e.g. componentTypes.Component1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC.DATA-ELEMENT-REF)
            else None
        """
        self.logger.info(f"[GUI:get_tv_elementPath()]: attempting to generate TreeView Element Path")
        if tv == None:
            self.logger.error("[GUI:get_tv_elementPath()]: tv is None")
            return None
        if tv_item == None:
            self.logger.error("[GUI:get_tv_elementPath()]: tv_item is None")
            return None
        tv_item_text = tv.item(tv_item, "text")
        if tv_item_text == None or tv_item_text == "":
            self.logger.error("[GUI:get_tv_elementPath()]: tv_item_text is empty")
            return None
        text_value = self.get_tv_text_value(tv_item_text)
        if text_value == None:
            self.logger.error("[GUI:get_tv_elementPath()]: tv_item Path not resolveable: last Element has no text value ")
            return None
        self.logger.info(f"[GUI:get_tv_elementPath()]: Input Parameters are valid. Proceeding to path generation")
        tv_item_tag = self.get_tv_tag_value(tv_item_text)

        AUTOSAR_path_in_elementPath = False  #True if there are AUTOSAR_Path short names in elementPath, else False
        elementPath = ""

        #generate elementPath from target_tv_item to first autosar path short name addressing
        self.logger.info(f"[GUI:get_tv_elementPath()]: generating path to first occurence of AUTOSAR Short Name addressing")
        while not AUTOSAR_path_in_elementPath and tv_item != None:
            tv_item_text = tv.item(tv_item,"text")

            tv_item_tag = self.get_tv_tag_value(tv_item_text)
            tv_item_AUTOSAR_path = self.get_tv_AUTOSAR_path_value(tv_item_text)
            if tv_item_AUTOSAR_path:

                AUTOSAR_path_in_elementPath = True
                if elementPath == "": elementPath = tv_item_AUTOSAR_path
                else: elementPath = f"{tv_item_AUTOSAR_path}.{elementPath}"
            else:
                if elementPath == "": elementPath = tv_item_tag
                else: elementPath = f"{tv_item_tag}.{elementPath}"

            tv_item = tv.parent(tv_item)
        self.logger.info(f"[GUI:get_tv_elementPath()]: found first occurence of AUTOSAR Short Name addresing. elementPath so far: {elementPath}")
        self.logger.info(f"[GUI:get_tv_elementPath()]: generating AUTOSAR Short Name addressing Path until root element")
        #generate AUTOSAR short name path part of elementPath
        while tv_item:
            tv_item_text = tv.item(tv_item,"text")
            tv_item_AUTOSAR_path = self.get_tv_AUTOSAR_path_value(tv_item_text)
            if not tv_item_AUTOSAR_path:
                tv_item = tv.parent(tv_item)
                continue
            if elementPath=="": elementPath=tv_item_AUTOSAR_path
            else: elementPath = f"{tv_item_AUTOSAR_path}.{elementPath}"
            
            tv_item = tv.parent(tv_item)

        #return elementPath
        if elementPath == "":
            self.logger.error("[GUI:get_tv_elementPath()]: Error generating filepath: filepath is empty String")
            return None
        self.logger.info(f"[GUI:get_tv_elementPath()]: element Path generation successful. returning {elementPath}")
        return elementPath
        
    def set_map_frame_domain_value_entry(self, event, tv, selected_domain_element_name, selected_domain_element_value):
        """
        set Stringvar selected_domain_element_name to the elementPath of the selected TreeView Item in tv
        :param tv: TreeView Object
        :param selected_domain_element_name: Stringvar that is linked to the text in map_domain_frame_name_entry
        :param selected_domain_element_value: Stringvar that is linked with the text in map_domain_frame_value_entry
        :return: Content of selected_domain_element_name and selected_domain_element_value
            Else None
        """
        self.logger.info(f"[GUI:set_map_frame_domain_value_entry()]: attempting to set Stringvars of domain_frame_content_frame")
        if tv == None:
            self.logger.error("[GUI:set_map_frame_domain_value_entry()]: TreeView Object is None")
            return None
        tv_selection = tv.selection()
        if tv_selection == None or len(tv_selection) != 1:
            self.logger.error("[GUI:set_map_frame_domain_value_entry()]: error fetching tv_selection: either None, or multiple items selected")
            return None
        if selected_domain_element_name == None:
            self.logger.error("[GUI:set_map_frame_domain_value_entry()]: selected_domain_element_name is None")
            return None
        self.logger.info(f"[GUI:set_map_frame_domain_value_entry()]: input parameters are valid. Proceeding to set Variables")
        tv_item_text = tv.item(tv_selection[0], "text")

        #check if selected Element is mappable and clear Selection if not
        tv_text = self.get_tv_text_value(tv_item_text)

        if tv_text == None:
            tv.selection_clear()
            selected_domain_element_name.set("")
            selected_domain_element_value.set("")
            return None  #alternative: selected_domain_element_name.get()?
        #get elementPath and display it in map_domain_frame_name_entry
        elementPath = self.get_tv_elementPath(tv, tv_selection[0])
        selected_domain_element_name.set(elementPath)
        selected_domain_element_value.set(tv_text)

        
        self.logger.info(f"[GUI:set_map_frame_domain_value_entry()]: variable setting successful: name = {selected_domain_element_name.get()}; value = {selected_domain_element_value}")
        return selected_domain_element_name.get(), selected_domain_element_value.get()

    def popup_conflict_manager(self, conflict_list, main_frame_conflict_manager=None):
        """
        generate ttk TopLevel Window to let the User decide which inconsistent values shall bee changed and
        what values are to be kept
        :param conflict_list: list of tuples of format: (sysml_element,[domain_elements],most_current_value)
            sysml_element: sysml element from mapping.json that is part of this conflict
            [mapped_domain_model_elements]: list of all domain model elements that are mapped to sysml_element
            most_current_value: value attribute of the first element with the highest "write_prio_value" or value attribute of sysml_element if "write_prio"==0 for all domain model elements
        :param main_frame_conflic_list: Frame to which the popup contents shall be loaded to. can be set for testing purposes
        :return: True on creation; on Button "button_apply_changes" press, MetadataManager.apply_value_changes_to_mapping is called to save changes to mapping.json
            None on error
        """
        self.logger.info(f"[GUI:popup_conflict_manager()]: attempting to generate and open conflict manager")
        #check format of conflict_list
        if not conflict_list:
            self.logger.error("[GUI:popup_conflict_manager()]: conflict_list is None")
            return None
        if not isinstance(conflict_list,list):
            self.logger.error("[GUI:popup_conflict_manager()]: conflict_list is not of type_list")
            return None
        if not all(isinstance(conflict,tuple) and len(conflict) == 3 
                   and isinstance(conflict[0],dict) and isinstance(conflict[1],list) 
                   and isinstance(conflict[2],str) 
                   and all(isinstance(domain_element,dict) for domain_element in conflict[1])
                   for conflict in conflict_list):
            self.logger.error("[GUI:popup_conflict_manager()]: conflict_list is not of type (dict,[dict],str))")
            return None

        if not main_frame_conflict_manager:
            #generate TopLevel Element
            popup = tk.Toplevel(self.main_frame)
            popup.title("Conflict Manager")
            popup.geometry("1500x1000")
            popup.grid_rowconfigure(0, weight=1)
            popup.grid_columnconfigure(0, weight=1)
            main_frame_conflict_manager =  ctk.CTkScrollableFrame(popup,fg_color="lightgrey")
            main_frame_conflict_manager.rowconfigure(0,weight=1)
            main_frame_conflict_manager.columnconfigure(0,weight=1)

        self.logger.info(f"[GUI:popup_conflict_manager()]: input parameters are valid. Proceeding to generate TopLevel Window")
        selection_list = []# Format [((sysml_elem_uuid,most_current_value),syml_checkbox_var),((domain_model_element_uuid,most_current_value),domain_model_element_checkbox_var),...]
        button_apply_changes = ctk.CTkButton(main_frame_conflict_manager, text="apply changes", command=lambda: popup.destroy() if self.mm.apply_value_changes_to_mapping(selection_list)==True else self.logger.error("could not apply changes in conflict manager"))
        self.logger.info(f"[GUI:popup_conflict_manager()]: Generating Conflict entry frames")
        for conflict_index, conflict in enumerate(conflict_list):
            conflict_entry_frame = self.generate_conflict_entry_frame(conflict,main_frame_conflict_manager,selection_list)
            #LAYOUT
            conflict_entry_frame.grid(row=conflict_index, column=0, padx=3, pady=3, sticky="nsew")

        #LAYOUT
        main_frame_conflict_manager.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")
        button_apply_changes.grid(row=len(conflict_list)+1, column=0, padx=3, pady=3, sticky="nsew")
        self.logger.info(f"[GUI:popup_conflict_manager()]: conflict manager creation successful")
        return True

    def generate_conflict_entry_frame(self, conflict, main_frame_conflict_manager, selection_list):
        """
        generate Frame that contains Conflict information for one conflict in conflict_list
        Format:
            Most current value according to write_prio: {most_current_value}
            SysMLv2-Element: {sysml_element['name']}/{sysml_element['uuid']}; value = {sysml_element['value']} Checkbox: update value to most current value
                Domain-Element: {domain_model_element['name']}/{domain_model_element['uuid']}; value = {domain_model_element['value']} Checkbox: update value to most current value
                ...
                Domain-Element: {domain_model_element['name']}/{domain_model_element['uuid']}; value = {domain_model_element['value']} Checkbox: update value to most current value
        :param conflict: conflict from selection list of format (sysml_element,[mapped_domain_elements],most_current_value)
            sysml_element: sysml element from mapping.json that is part of this conflict
            [mapped_domain_model_elements]: list of all domain model elements that are mapped to sysml_element
            most_current_value: value attribute of the first element with the highest "write_prio_value" or value attribute of sysml_element if "write_prio"==0 for all domain model elements
        :param main_frame_conflict_manager: parent Frame to which the conflict frame shall be added to
        :param selection_list: list of tuples ((model_element_uuid, new_value),selection_var)
            model_element_uuid: uuid of a model_element that is part of any conflict in conflict_list
            new value: value to which the elements value must be changed to, if the user selects it
            selection_var: Stringvar. If 1: values must be changed, if 0: value must not be changed
            This list shall be appended with new entries of that format for each model element that is part of this conflic
        :return: CTkFrame of Format specified above
        """
        self.logger.info(f"[GUI:generate_conflict_entry_frame()]: attemting to generate conflict entry frame")
        if  conflict==None or main_frame_conflict_manager == None or selection_list == None:
            self.logger.error("[GUI:generate_conflict_entry_frame()]: one Parameter is None")
            return None

        if not (isinstance(conflict,tuple) and len(conflict) == 3 and 
                isinstance(conflict[0],dict) and isinstance(conflict[1],list) and 
                isinstance(conflict[2],str) and all(isinstance(domain_model_element,dict) for domain_model_element in conflict[1])):
            self.logger.error("[GUI:generate_conflict_entry_frame()]: Conflict is not of Type (dict,[dict],str)")
            return None

        (sysml_element, domain_model_elements, most_current_value) = conflict
        self.logger.info(f"[GUI:generate_conflict_entry_frame()]: input parameters are Valid. Current Conflict sysml element uuid = {sysml_element["uuid"]}. Proceeding to generate Frame")
        #create conflict frame
        conflict_frame = ctk.CTkFrame(main_frame_conflict_manager, fg_color="lightgrey")
        conflict_frame.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")
        conflict_frame.columnconfigure(0, weight=1)
        #create most current value and sysml label and checkbox
        sysml_checkbox_var = StringVar(value="0")
        label_most_current = ctk.CTkLabel(conflict_frame, text=f"Most current value according to write_prio: {most_current_value}", height=30, font=("default",14), text_color="black",anchor="w",justify="left")
        label_sysml_name_uuid_value = ctk.CTkLabel(conflict_frame, text=f"SysMLv2-Element:\n    File: {sysml_element['filePath']}\n    ElementPath: {sysml_element['elementPath']}\n    value: {sysml_element['value']}\n    write_prio: {sysml_element["write_prio"]}", height=30, font=("default",14), text_color="black",anchor="w",justify="left")
        checkbox_sysml = ctk.CTkCheckBox(conflict_frame, text="update value to most current value",variable=sysml_checkbox_var, text_color='black')

        #append selection list with sysml element data
        selection_list.append(((sysml_element["uuid"],most_current_value),sysml_checkbox_var))

        #iterate through domain_model_elements and create domain model element labels, checkboxes and append domain model element data to selection list
        for domain_model_element_index, domain_model_element in enumerate(domain_model_elements):
            domain_model_element_checkbox_var = StringVar(value="0")
            label_domain_model_element_name_uuid_value = ctk.CTkLabel(conflict_frame,text=f"    Domain-Element:\n        File: {domain_model_element['filePath']}\n        ElementPath: {domain_model_element['elementPath']}\n        value: {domain_model_element['value']}\n        write_prio: {domain_model_element["write_prio"]}", height=30, font=("default", 14), text_color="black",anchor="w",justify="left")
            checkbox_domain_model_element = ctk.CTkCheckBox(conflict_frame, text="update value to most current value", variable=domain_model_element_checkbox_var, text_color='black')
            selection_list.append(((domain_model_element["uuid"],most_current_value),domain_model_element_checkbox_var))

            #LAYOUT
            label_domain_model_element_name_uuid_value.grid(row=domain_model_element_index+2, column=0, padx=3, pady=3, sticky="nsew")
            checkbox_domain_model_element.grid(row=domain_model_element_index+2, column=1, padx=3, pady=3, sticky="nsew")

        #LAYOUT
        label_most_current.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")
        label_sysml_name_uuid_value.grid(row=1, column=0, padx=3, pady=3, sticky="nsew")
        checkbox_sysml.grid(row=1, column=1, padx=3, pady=3, sticky="nsew")
        self.logger.info(f"[GUI:generate_conflict_entry_frame()]: Conflcit frame generation successful")
        return conflict_frame
    
    def popup_mapping_editor(self,main_frame_mapping_editor=None):
        """
        Mapping:
            generate Toplevel window that displays all mappings in mapping.json in the follwing format:
            SysMLv2-Element
                parameters
            Domain model element:
                parameters
            Button: "remove mapping"
        Mapping:
            ....
            :param main_frame_mapping_editor: Frame to which the content will be loaded to. can be set for testing purposes
        :returns: True if generation was successful
        """
        self.logger.info(f"[GUI:popup_mapping_editor()]: attemtpting to generate and open mapping editor")
        if not main_frame_mapping_editor:

            #setup Toplevel and main frame
            popup = tk.Toplevel(self.main_frame)
            popup.title("Mapping Overview")
            popup.geometry("1500x1000")
            popup.grid_rowconfigure(0, weight=1)
            popup.grid_columnconfigure(0, weight=1)


            main_frame_mapping_editor = ctk.CTkScrollableFrame(popup,fg_color="lightgrey", width=900,height=500)
        
        mapping_list = self.mm.get_Mappings_elements()

        #generate mapping entry frames for each mapping
        self.logger.info(f"[GUI:popup_mapping_editor()]: generate mapping entry frames")
        for mapping_index, mapping in enumerate(mapping_list):
            mapping_entry_frame = self.generate_mapping_entry_frame(mapping,main_frame_mapping_editor)
            #LAYOUT
            mapping_entry_frame.grid(row=mapping_index, column=0, padx=3, pady=3, sticky="nsew")

        #LAYOUT
        main_frame_mapping_editor.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")
        self.logger.info(f"[GUI:popup_mapping_editor()]: mapping editor generation succesful")
        return True

    def generate_mapping_entry_frame(self, mapping, main_frame_mapping_editor):
        """
        generate mapping frame for specified mapping and return it with parent=main_frame_mapping_editor
        :param mapping: Tuple of Format (mapping_element, sysml_element, domain_model_element)
            mapping_element: "Mappings" element from mapping.json
            sysml_element: sysml element to which the mapping_element refers to
            domain_model_element: Domain model element to which the mapping_element refers to
        :param main_frame: CTkFrame to which the mapping entry frame shall be a child
        :return: mapping entry frame
            None on error
        """
        self.logger.info(f"[GUI:generate_mapping_entry_frame()]: attemting to generate mapping entry frames")
        # get mapping data from metadata manager
        if not (isinstance(mapping,tuple) and len(mapping) == 3 and 
                isinstance(mapping[0],dict) and isinstance(mapping[1],dict) and 
                isinstance(mapping[2],dict)):
            self.logger.error("[GUI:generate_mapping_entry_frame()]: mapping is not of Type (dict,dict,dict)")
            return None
        (mapping_element, sysml_element, domain_model_element) = mapping
        self.logger.info(f"[GUI:generate_mapping_entry_frame()]: input parameters are valid. Mapping is target_element = {sysml_element["uuid"]}, source_element = {domain_model_element["uuid"]}. Proceeding to generate Frame")
        #generate mapping entry frame
        mapping_frame = ctk.CTkFrame(main_frame_mapping_editor, fg_color="lightgrey")
       
        sysml_info_text = "Mapping:\n    SysMLv2 Element:\n"
        for key,value in sysml_element.items():
            sysml_info_text = f"{sysml_info_text}        {key}: {value}\n"
        domain_model_element_info_text = "    Domain Model Element:\n"
        for key,value in domain_model_element.items():
            domain_model_element_info_text = f"{domain_model_element_info_text}        {key}: {value}\n"
        label_sysml_info = ctk.CTkLabel(mapping_frame,text=sysml_info_text, height=30, font=("default", 14), text_color="black",anchor="w",justify="left")
        label_domain_model_element_info = ctk.CTkLabel(mapping_frame,text=domain_model_element_info_text, height=30, font=("default", 14), text_color="black",anchor="w",justify="left")

        button_remove_mapping = ctk.CTkButton(mapping_frame, text=f"remove mapping", 
                                             command=lambda: mapping_frame.destroy() if self.mm.remove_mapping(sysml_element["uuid"],domain_model_element["uuid"])==True else self.logger.error("could not remove mapping_entry"))

        #LAYOUT
        label_sysml_info.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")
        label_domain_model_element_info.grid(row=1, column=0, padx=3, pady=3, sticky="nsew")
        button_remove_mapping.grid(row=2, column=0, padx=3, pady=3, sticky="nsew")
        self.logger.info(f"[GUI:generate_mapping_entry_frame()]: mapping entry frame generation successful")
        return mapping_frame

    def popup_change_log(self, main_frame_change_log_viewer=None):
        """
        Generate Toplevel Window that shows all value changes for Values in mapping.json
        """
        self.logger.info(f"[GUI:popup_mapping_editor()]: attemtpting to generate and open mapping editor")
        if not main_frame_change_log_viewer:

            #setup Toplevel and main frame
            popup = tk.Toplevel(self.main_frame)
            popup.title("Change Log")
            popup.geometry("1500x1000")
            popup.grid_rowconfigure(0, weight=1)
            popup.grid_columnconfigure(0, weight=1)


            main_frame_change_log_viewer = ctk.CTkScrollableFrame(popup,fg_color="lightgrey", width=900,height=500)
        
        change_log = self.mm.get_change_log()

        #generate mapping entry frames for each mapping
        self.logger.info(f"[GUI:popup_mapping_editor()]: generate mapping entry frames")
        for idx, (changelog_element_uuid,change_log_element) in enumerate(change_log.items()):
            change_log_element_frame = self.generate_change_log_element_frame(change_log_element,changelog_element_uuid,main_frame_change_log_viewer)
            #LAYOUT
            change_log_element_frame.grid(row=idx, column=0, padx=3, pady=3, sticky="nsew")

        #LAYOUT
        main_frame_change_log_viewer.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")
        self.logger.info(f"[GUI:popup_mapping_editor()]: mapping editor generation succesful")
        return True
    
    def generate_change_log_element_frame(self,changelog_element,changelog_element_uuid,main_frame_change_log_viewer):
        """
        generate Frame of Format:
            Changes for Element:
                file: ...
                elementPath: ...
                    timestamp: value: {new_value} ({changed_by})
                    ....
        :param changelog_element: list of changes for changelog element with uuid = changelog_element_uuid
        :param changelog_element_uuid: uuid of mapping elements to which the change history applies
        :param main_frame_change_log_viewer: parent_frame
        :return: change_log_element_frame
        """
        self.logger.info(f"[GUI:generate_change_log_element_frame()]: generating change_log_element entry frame for element with uuid = {changelog_element_uuid}")

        if changelog_element == None or not (isinstance(changelog_element,list) and all(isinstance(changelog_element_item,dict) for changelog_element_item in changelog_element)):
            self.logger.error(f"[GUI:generate_change_log_element_frame()]: invalid changelog_element: {changelog_element}")
            return False
        if changelog_element_uuid == None or changelog_element_uuid == "":
            self.logger.error(f"[GUI:generate_change_log_element_frame()]: invalid changelog_element_uuid: {changelog_element_uuid}")
            return False
        if main_frame_change_log_viewer == None:
            self.logger.error(f"[GUI:generate_change_log_element_frame()]: invalid parent frame: None")
            return False

        self.logger.info(f"[GUI:generate_change_log_element_frame()]: input parameters are valid. proceeding")
        change_log_element_frame = ctk.CTkFrame(main_frame_change_log_viewer, fg_color="lightgrey")
       
        change_log_element_in_mapping = self.mm.get_model_element(changelog_element_uuid)
        
        change_log_element_text = f"Changes for Element:\n    file: {change_log_element_in_mapping["filePath"]}\n    element path: {change_log_element_in_mapping["elementPath"]}\n"
        for change_log_item in changelog_element:
            change_log_element_text = f"{change_log_element_text}        {change_log_item["timestamp"]}: value: {change_log_item["value"]} ({change_log_item["changed_by"]})\n"
        change_log_element_text = f"{change_log_element_text}\n"

        label_domain_model_element_info = ctk.CTkLabel(change_log_element_frame,text=change_log_element_text, height=30, font=("default", 14), text_color="black",anchor="w",justify="left")
        
        #LAYOUT
        label_domain_model_element_info.grid(row=1, column=0, padx=3, pady=3, sticky="nsew")
        self.logger.info(f"[GUI:generate_change_log_element_frame()]: change_log_element entry frame generation successful")
        return change_log_element_frame
        
def main(): 
    
    # Run Initial Log Setup for debugging
    setup_logging() 
    # Docker Check
    check_docker()  # Check if Docker is installed and running
 
    # Initialize DockerManager to build the Neo4j database and Syson visualization Docker container
    docker = DockerManager()
    docker.start_docker_services()

    # Load Default Config File from config folder   
    DEFAULT_CONFIG_FILE = "config/default_config.json" 
    DEFAULT_CONFIG = load_config(DEFAULT_CONFIG_FILE)

    current_working_dir = "./example/working_dir/"
    # Create Parser object classes for functions that can read, parse and edit these specific files
    fp_sysml = SysmlParser(sysml_path=f"{current_working_dir}sysml_file.sysml") # #"models/se_domain/example_drone_origin.sysml"
    fp_code = CodeParser(code_file_path = "models/sw_domain/generated_code.py")
    fp_gerber = GerberParser(gerber_file_path=f"{current_working_dir}example.gbrjob")
    fp_step = StepParser(step_file_path="models/me_domain/STEP_AgriUAV.stp")
    fp_AUTOSAR = AUTOSAR_Parser(AUTOSAR_file_path=f"{current_working_dir}example.arxml")
    vc = VersionControl(config=DEFAULT_CONFIG)
    mm = MetadataManager(config=DEFAULT_CONFIG, versioncontrol=vc, gerberparser=fp_gerber, stepparser=fp_step, codeparser=fp_code, AUTOSARparser=fp_AUTOSAR, sysmlparser=fp_sysml)
    mapping_file_path = f"{current_working_dir}mapping.json"
    change_log_file_path = f"{current_working_dir}change_log.json"
    mm.mapping_file_path= mapping_file_path
    fp_AUTOSAR.mapping_file_path = mapping_file_path
    mm.change_log_path = change_log_file_path

    # Start the Tkinter app
    app = GUI(config=DEFAULT_CONFIG, metadatamanager=mm, versioncontrol=vc)

    # Automatic update (fetching new data from domain files and writing new values to sysmlv2 model and mapping file)
    mm.app = app
    mm.update_sysml_model()

    app.root.mainloop() 

if __name__ == "__main__":
    main() 
