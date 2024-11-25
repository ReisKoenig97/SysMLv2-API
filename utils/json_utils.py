import json

def load_json(file_path):
    """
    Loads JSON data from a file.

    Args:
        file_path (str): The path to the JSON file to be loaded.

    Returns:
        dict: The loaded JSON data or None if an error occurred.
    """
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except IOError as e:
        print(f"Error loading JSON from {file_path} in {__name__}: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path} in {__name__}: {e}")
        return None


def save_json(file_path, data):
    """
    Saves data to a JSON file.

    Args:
        file_path (str): The path where the JSON file should be saved.
        data (dict): The data to be saved in the JSON file.

    Returns:
        bool: True if the save was successful, False otherwise.
    """
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    except IOError as e:
        print(f"Error saving JSON to {file_path} in {__name__}: {e}")
        return False
