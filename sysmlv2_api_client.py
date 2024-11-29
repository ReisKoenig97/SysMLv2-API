import logging
from utils.json_utils import save_json
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
        # Logs from this file getting collected from the main file with name: sysmlv2_api_client
        self.logger = logging.getLogger(__name__) 
        self.logger.info(f"Initializing API Client with URL: {base_url}")

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
        self.logger.debug(f"Fetching model with ID: {model_id}")

        try:
            response = requests.get(f"{self.base_url}/models/{model_id}")
            response.raise_for_status()  # Raise an error if the status code is not 200
            self.logger.info(f"Successfully fetched model {model_id}")
            return response.json()
        except requests.RequestException as e:
            self.logger.error(f"Error fetching model {model_id}: {e}")
            raise 

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
        
        file_path = "./models/se_domain/example_sysmlv2_model.json"
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
