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

    # TODO 
    # Check the generated URL for gfetting the model data inside the database 
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
        Saves the API response into a JSON file using the json_utils 

        Args:
            data (dict): The JSON data to be saved.
            file_path (str): The file path where the data should be saved.
        """
        if save_json(file_path=file_path, data=data):
            print(f"SysML response (JSON) '{file_path}' saved successfully. ({__name__}.save_response)")
        else:
            print(f"Error saving SysML response (JSON) to {file_path} in {__name__}")

    def create_model_project(self): 
        """
        Creates an initial sysmlv2 model as a project a POST request to given URL (here base local server url).
        It is not needed to provide a header since the request library automatically chooses the best (currenty working)
        """
        
        file_path = "./models/example_sysmlv2_model.json"
        url = "http://localhost:9000/projects"

        try: 
        
            with open(file_path, 'r') as file:
                model_content = file.read()
                print(model_content +"\n"+" with data type: ", type(model_content))
                response = requests.post(url=url, headers={'Content-Type': 'application/json'}, json={"model": model_content})

                #response = requests.post(self.base_url, files=model)

                if response.status_code == 200: 
                    print("Successfully uploaded model!")
                    return response.json() 
                else: 
                    print("Failed to upload model")
                    return None

        except Exception as e: 
            raise e

    


class SysMLv2App:
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
        self.root = root
        self.root.title("SysMLv2 API Client")

        # Initialize the API client
        self.api_client = api_client 

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        """Creates the GUI elements."""
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

    api_client = SysMLv2APIClient(base_url=DEFAULT_CONFIG["base_url"])
    api_client.create_model_project()
    

    # Start the Tkinter app
    #root = tk.Tk()
    #app = SysMLv2App(root, api_client=api_client)
    #root.mainloop() 

if __name__ == "__main__":
    main() 
