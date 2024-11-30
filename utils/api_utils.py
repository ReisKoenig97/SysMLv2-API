import requests
import logging

def send_request(method, url, data=None, headers=None, params=None):
    """
    Generalized method to send HTTP requests.
    
    Args:
        method (str): HTTP method (e.g., "POST", "GET", "PUT", "DELETE").
        url (str): The URL for the API call.
        data (dict, optional): The JSON data to send in the request body.
        headers (dict, optional): The headers for the request.
        params (dict, optional): The query parameters for the request.

    Returns:
        dict: JSON response if successful, None otherwise.
    """
    logger = logging.getLogger("api_utils")
    try:
        response = requests.request(method, url, headers=headers, json=data, params=params)
        logger.debug(f"Request to {url} with method={method}, data={data}, params={params}")
        
        if response.status_code == 200:
            logger.info(f"Request to {url} succeeded.")
            return response.json()
        else:
            logger.error(f"Request to {url} failed with status code {response.status_code}: {response.text}")
            return None
    except requests.RequestException as e:
        logger.error(f"Error during request to {url}: {e}")
        return None
