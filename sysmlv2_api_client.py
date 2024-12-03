import logging
from utils.api_utils import send_request
from utils.json_utils import load_json, save_json
import requests
#import pprint 



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
        # Logs from this file getting collected from the main file with name: sysmlv2_api_client
        self.logger = logging.getLogger(__name__) 
        self.logger.info(f"Initializing API Client with URL: {base_url}")

        self.base_url = base_url 
        self.se_file_path = "./models/se_domain"

    # TODO 
    # Check the generated URL for gfetting the model data inside the database 
    def get_project(self, project_id: str) -> dict:
        """
        Fetches a SysMLv2 model with the given ID.

        Args:
            project_id (str): The ID of the desired model.

        Returns:
            dict: The model as JSON data if retrieval is successful.
        """
        self.logger.debug(f"Fetching model with ID: {project_id}")
        
        # 1) Change Endpoint URL 
        get_project_url = f"{self.base_url}/projects/{project_id}" 
        # 2) Use send_request method from api_utils. Returns JSON response if successful, None otherwise.
        get_project_response = send_request("GET",url=get_project_url, 
                                                  headers={"Content-Type" : "application/json"})
        # 3) Additional Logs and Prints 
        if get_project_response: 
            self.logger.info(f"Successfully fetched project with id {project_id}. ({__name__}.get_project)")
            ##print("Fetched Project: ", get_project_response)
        else: 
            self.logger.error(f"Failed to fetch project with ID {project_id}. ({__name__}.get_project)")

    def save_response(self, data: dict, file_path: str):
        """
        Saves the API response into a JSON file using the json_utils 

        Args:
            data (dict): The JSON data to be saved.
            file_path (str): The file path where the data should be saved.
        """ 
        # Uses the json_utils to save json. Here it only provides additional information 
        if save_json(file_path=file_path, data=data):
            self.logger.info(f"SysML response (JSON) '{file_path}' saved successfully. ({__name__}.save_response)")
        else:
            self.logger.error(f"Error saving SysML response (JSON) to {file_path}. ({__name__}.save_response)")


    def create_model(self): 
        """
        Creates an initial sysmlv2 model as a project with a POST request to the given URL (here base local server URL).
        It is not needed to provide a header since the request library automatically chooses the best (currently working).
        """
        self.logger.debug(f"Creating new model and send a POST request")
        # 1) Change filepath to be uploaded
        file_path = f"{self.se_file_path}/example_sysmlv2_model.json"
        # 2) Change Endpoint URL 
        create_model_url = f"{self.base_url}/projects"
        # 3) Load the data from file_path as JSON 
        create_model_data = load_json(file_path) 
        # 4) Use send_request method from api_utils. Returns JSON response if successful, None otherwise.
        create_model_post_response = send_request("POST",url=create_model_url, headers={"Content-Type" : "application/json"}, 
                                                   data=create_model_data)
        # 5) Additional Logs and Prints 
        if create_model_post_response: 
            self.logger.info(f"Successfully uploaded new model from {file_path}. ({__name__}.create_model)")
            #print("New Model created: ", create_model_post_response)
        else: 
            self.logger.error(f"Failed to upload new model. ({__name__}.create_model)")
        

    def create_commit(self, project_id): 
        """
        Sends (POST) a commit response to given URL.
        """
        self.logger.debug("Commit Changes to the Server API")
        # 1) Change filepath to be uploaded
        file_path = "./models/se_domain/example_sysmlv2_commit.json" 
        # 2) Change Endpoint URL 
        commit_url = f"{self.base_url}/projects/{project_id}/commits"
        # 3) Load the data from file_path as JSON 
        commit_data= load_json(file_path)
        # 4) Use send_request method from api_utils. Returns JSON response if successful, None otherwise.
        commit_post_response = send_request("POST",url=commit_url, 
                                             headers={"Content-Type": "application/json"},
                                             data=commit_data)
        # 5) Additional Logs and Prints 
        if commit_post_response: 
            self.logger.info(f"Successfully uploaded new commit from {file_path} with model id {project_id}. ({__name__}.create_commit)")
            #print("New Commit created: ", commit_post_response)
        else: 
            self.logger.error(f"Failed to upload new commit. ({__name__}.create_commit)")

    def get_model_by_id(self):
        """Fetches a model and saves the response."""
        project_id = self.project_id_entry.get()

        if not project_id:
            self.logger.warning("Fetch model attempted without entering a Model ID")
            #messagebox.showwarning("Warning", "Please enter a Model ID.")
            return

        try:
            self.logger.info(f"Attempting to fetch model with ID: {project_id}")
            # Fetch the model
            data = self.api_client.get_model(project_id)
            #messagebox.showinfo("Success", f"Model {project_id} successfully fetched!")

            # Save the response
            save_path = os.path.join(os.getcwd(), f"{project_id}_model.json")
            self.api_client.save_response(data, save_path)
            #messagebox.showinfo("Saved", f"Model has been saved at:\n{save_path}")
        except ConnectionError as e:
            self.logger.error(f"Connection error while fetching model {project_id}: {e}")
            #messagebox.showerror("Connection Error", str(e))
        except IOError as e:
            self.logger.error(f"File save error for model {project_id}: {e}")
            # messagebox.showerror("Save Error", str(e))
