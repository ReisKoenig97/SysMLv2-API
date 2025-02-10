#from utils import json_utils 
from utils.json_utils import load_json, save_json 
import os 
import logging

def save_config(config_file_path, config_data_dict):
    """
    Saves the configuration data to the specified JSON file.

    Args:
        config_file_path (str): The path to the configuration file to be saved.
        config_data_dict (dict): The configuration data to save in the JSON file.

    Returns:
        bool: Returns True if the file was saved successfully, otherwise False.

    Raises:
        IOError: If there is an error writing the config file.
    """
    logger = logging.getLogger("config_utils: save_config")
    try:
        # Create directories 'config' if they don't exist
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        
        # Use save_json from json_utils to save the configuration data
        if save_json(config_file_path, config_data_dict):
            logger.info(f"Config file '{config_file_path}' saved successfully. ({__name__}.save_config)")
            return True
        else:
            return False
    except IOError as e:
        print(f"Error saving the config file: {e} raised in {__name__}.save_config()")
        return False


def load_config(config_file_path="config/default_config.json"):
    """
    Loads the configuration from a JSON file. If the file does not exist, it will 
    create the configuration file with default settings.

    Args:
        config_file_path (str): The path to the configuration file to be loaded. 
                                Defaults to 'config/default_config.json'.

    Returns:
        dict or None: Returns the configuration as a dictionary if the file exists.
                      Returns None if the file doesn't exist or if an error occurs.
    
    Raises:
        IOError: If there is an error reading the config file.
    """
    logger = logging.getLogger("config_utils: load_config")
    # Check if the config file exists
    if not os.path.exists(config_file_path):
        # If the file doesn't exist, create it with default settings
        default_config_dict = {
            "base_url": "http://localhost:9000/docs/"
        }
        
        # Call the save_config function to save the default configuration
        if save_config(config_file_path, default_config_dict):
            logger.debug(f"Cannot find Default config ... Created new file at '{config_file_path}'.")
            return default_config_dict
        else:
            logger.debug(f"Failed to create default config at '{config_file_path}'.")
            return None

    # If the config file exists, load and return its content using load_json
    try:
        config_data = load_json(config_file_path)
        if config_data is not None:
            #logger.info(f"Config file '{config_file_path}' loaded successfully.")
            return config_data
        else:
            logger.error(f"Error loading config file '{config_file_path}' in {__name__}.load_config()")
            return None
    except Exception as e:
        logger.error(f"Error reading the config file '{config_file_path}': {e} raised in {__name__}.load_config()")
        return None

