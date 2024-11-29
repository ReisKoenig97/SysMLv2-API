import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import logging

# Utils and module references

from sysmlv2_api_client import SysMLv2APIClient
from utils.config_utils import save_config, load_config
from utils.json_utils import save_json, load_json

# External Libraries has to be installed in the local git folder / venv 
#import requests

# Initial centralized Logging Setup to control all logs. Takes all logs from each .py file etc
def setup_logging(): 
    logging.basicConfig(
        level=logging.DEBUG, # Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format="%(asctime)s - (name)s - %(levelname)s - %(message)s - %(pathname)s - Line: %(lineno)d", # Log format 
        handlers=[
            logging.FileHandler("app.log"), # Write Logs in file 'app.log'
            logging.StreamHandler() # Write Logs to Console
        ]
    )

class SysMLv2GUI:
    """
    Main application for the GUI, managing user interaction.
    Uses Tkinter for the user interface.
    """
    def __init__(self, root, api_client):
        """
        Initializes the Tkinter GUI.

        Args:
            root: The main window of the application.
        """
        self.logger = logging.getLogger(__name__)


        self.root = root
        self.root.title("SysMLv2 API Client")

        # Initialize the API client
        self.api_client = api_client 

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        """Creates the GUI elements."""

        self.logger.debug(f"Creating Widgets for SysMLv2GUI")

        # Use own ttk style to avoid visual issues (e.g. macOS darkmode)
        style = ttk.Style()
        style.theme_use('default')

        # Input for Model ID
        ttk.Label(self.root, text="Model ID:").grid(row=0, column=0, padx=5, pady=5)
        self.model_id_entry = ttk.Entry(self.root, width=30)
        self.model_id_entry.grid(row=0, column=1, padx=5, pady=5)

        # Button to fetch the model
        fetch_button = ttk.Button(self.root, text="Fetch Model", command=self.fetch_model)
        fetch_button.grid(row=1, column=0, columnspan=2, pady=10)

    def fetch_model(self):
        """Fetches a model and saves the response."""
        model_id = self.model_id_entry.get()

        if not model_id:
            self.logger.warning("Fetch model attempted without entering a Model ID")
            messagebox.showwarning("Warning", "Please enter a Model ID.")
            return

        try:
            self.logger.info(f"Attempting to fetch model with ID: {model_id}")
            # Fetch the model
            data = self.api_client.get_model(model_id)
            messagebox.showinfo("Success", f"Model {model_id} successfully fetched!")

            # Save the response
            save_path = os.path.join(os.getcwd(), f"{model_id}_model.json")
            self.api_client.save_response(data, save_path)
            messagebox.showinfo("Saved", f"Model has been saved at:\n{save_path}")
        except ConnectionError as e:
            self.logger.error(f"Connection error while fetching model {model_id}: {e}")
            messagebox.showerror("Connection Error", str(e))
        except IOError as e:
            self.logger.error(f"File save error for model {model_id}: {e}")
            messagebox.showerror("Save Error", str(e))





def main(): 
    # Run Initial Log Setup
    setup_logging() 

    DEFAULT_CONFIG_FILE = "config/default_config.json" # Change config file path here 

    # Load Default Config File from config folder
    DEFAULT_CONFIG = load_config(DEFAULT_CONFIG_FILE)

    api_client = SysMLv2APIClient(base_url=DEFAULT_CONFIG["base_url"])
    api_client.create_model_project()
    

    # Start the Tkinter app
    #root = tk.Tk()
    #app = SysMLv2GUI(root, api_client=api_client)
    #root.mainloop() 

if __name__ == "__main__":
    main() 
