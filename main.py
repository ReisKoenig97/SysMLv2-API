import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
#from .utils import config_utils,json_utils
from utils.config_utils import save_config, load_config
from utils.json_utils import save_json, load_json

# External Libraries has to be installed in the local git folder / venv 
import requests

class SysMLv2APIClient:
    """
    Class to interact with the SysMLv2 API.
    Connects to the local server, performs CRUD operations,
    and saves the results.

    Attributes:
        base_url (str): Base URL of the API.
    """
    def __init__(self, base_url: str):
        """
        Initializes the API client with the given base URL.

        Args:
            base_url (str): The base URL of the local SysMLv2 server.
        """
        self.base_url = base_url 

    def get_model(self, model_id: str) -> dict:
        """
        Fetches a SysMLv2 model with the given ID.

        Args:
            model_id (str): The ID of the desired model.

        Returns:
            dict: The model as JSON data if retrieval is successful.
        """
        try:
            response = requests.get(f"{self.base_url}/models/{model_id}")
            response.raise_for_status()  # Raise an error if the status code is not 200
            return response.json()
        except requests.RequestException as e:
            raise ConnectionError(f"Error fetching the model: {e}") from e

    def save_response(self, data: dict, file_path: str):
        """
        Saves the API response into a JSON file.

        Args:
            data (dict): The JSON data to be saved.
            file_path (str): The file path where the data should be saved.
        """
        try:
            with open(file_path, "w") as file:
                json.dump(data, file, indent=4)
        except IOError as e:
            raise IOError(f"Error saving the file: {e}") from e


class SysMLv2App:
    """
    Main application for the GUI, managing user interaction.
    Uses Tkinter for the user interface.
    """
    def __init__(self, root):
        """
        Initializes the Tkinter GUI.

        Args:
            root: The main window of the application.
        """
        self.root = root
        self.root.title("SysMLv2 API Client")

        # Initialize the API client
        self.api_client = SysMLv2APIClient(base_url="http://localhost:8080")

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        """Creates the GUI elements."""
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
            messagebox.showwarning("Warning", "Please enter a Model ID.")
            return

        try:
            # Fetch the model
            data = self.api_client.get_model(model_id)
            messagebox.showinfo("Success", f"Model {model_id} successfully fetched!")

            # Save the response
            save_path = os.path.join(os.getcwd(), f"{model_id}_model.json")
            self.api_client.save_response(data, save_path)
            messagebox.showinfo("Saved", f"Model has been saved at:\n{save_path}")
        except ConnectionError as e:
            messagebox.showerror("Connection Error", str(e))
        except IOError as e:
            messagebox.showerror("Save Error", str(e))


class MetadataManager:
    """
    Class to manage metadata between domain models and SysMLv2.
    """
    def __init__(self, domain_files: list):
        """
        Initializes the metadata manager.

        Args:
            domain_files (list): List of standardized file paths from domains.
        """
        self.domain_files = domain_files

    def map_metadata(self, sysml_data: dict, domain_data: dict) -> dict:
        """
        Links metadata from domain models with SysMLv2 data.

        Args:
            sysml_data (dict): SysMLv2 data in JSON format.
            domain_data (dict): Domain model data in JSON format.

        Returns:
            dict: Combined metadata.
        """
        # Example logic: Combine the data
        combined_data = {
            "sysml": sysml_data,
            "domain": domain_data
        }
        return combined_data


def main(): 

    DEFAULT_CONFIG_FILE = "config/default_config.json" # Change config file path here 

    # Load Default Config File from config folder
    DEFAULT_CONFIG = load_config(DEFAULT_CONFIG_FILE)

    

    # Start the Tkinter app
    root = tk.Tk()
    app = SysMLv2App(root)
    root.mainloop()

if __name__ == "__main__":
    main() 
