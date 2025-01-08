import logging 
import re #regex for parsing 
from utils.json_utils import load_json


# Contains all standardized (for this masters thesis) file parser as a single class for each file format 
# Each class should have methods to read, load, save, and extract metadata
# Use 'json_utils' to standardize json file handling such as reading, writing and saving JSON files 

class Sysml_parser: 
    # Parses specific sysml files by getting "metadata" / "@" (abreviation)
    """
    TODO: 
    1) Query SysMLv2 File for 'metadata' or '@' with regex; Metadata acts basically like a tag
        1.1) If found metadata -> Display User the metadata
            1.1.1) Wait until user selects metadata so that the tagged data can be prepared/extracted 
                    for the domain engineer -> only gets "his view of the system with the relevant data"
            1.1.2) Script generated a view (better package by using in-built element filters) based on tagged data 

        1.2) If not found metadata -> Display User that no metadata was found
            1.2.1) User can manually tag data by getting a view of the sysml file with selectable/clickable
                    elements that can be tagged with metadata
            1.2.2) Script generates 
                a) 'metadata def <user variable>
                b) '<user variable> about ...' 
                c) view based on tagged data (analogue to 1.1.2)

    2) Prepare / Extract tagged metadata: 
        here we need to identify if the tagged data is a part, item etc to compare 
        Is the metadata used with the libraries or fully custom? 
        Use Element Filters (graphical representation) 
        Use a recursive import to include all nested elements that are tagged by metadata 'about'
    """

    def __init__(self):
        pass 
        

class Gerber_parser:    
    # Parses specific files (Gerber X2/3) from the E/E Engineering Domain 
    """
    TODO: 
    1) Read gerber file 
    2) Parse through and extract metadata 
    3) Save Metadata in JSON Formatted file 
    """
    def __init__(self, file_path):
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"Initial gerber_parser")
        # Contains extracted informations of parsed gerber file 
        self.data = {}
        # Path to gerber file to be parsed
        self.file_path = file_path

    def parse_gerber_job_file(self, sections: list[str], keywords: list[str]):
        """
        Reads, extracts and saves gerber file metadata

        Args:
        sections (list[str]): List of main objects to search in ('Header', 'GeneralSpecs', 'DesignRules', 'MaterialStackup', 'FilesAttributes').
        keywords (list[str]): List of keywords to search for inside the specified sections.

        Returns: dict  when successful parsed, else empty dict
        """ 
        # Helper function 
        def search_keywords(data , keywords, parent_key = ""): 
            """
            Recursively searches for specified keywords in a nested JSON structure
            Args:
                data (dict) : data to search inside
                keywords (list[str]) : list of words to search for inside the file (JSON)
                parent_key (str) : Current path of keys 
            Returns: 
                dict : Contains found key-value pairs matching the keywords
            """
            found_data = {}
            # Case 1: Check if data is a dict (has nested properties)
            if isinstance(data, dict): 
                for key, value in data.items():
                    # Set the current key and their parent (if it has a parent)   
                    new_key = f"{parent_key}.{key}" if parent_key else key
                    # Check if we found any keyword from the given keywords list inside for each keyword in the line 
                    if any(keyword in key for keyword in keywords): 
                        # Adding the value to the key
                        found_data[new_key] = value 
                    # After adding the key-value pair. Recursively check if that value has properties as well / has '{ ... }'
                    found_data.update(search_keywords(data=value, keywords=keywords, parent_key=new_key))
            # Case 2: Each item inside the list is a dict, therefore looping through each dict 
            elif isinstance(data, list):
                for index, item in enumerate(data): 
                    found_data.update(search_keywords(data=item, keywords=keywords, parent_key=f"{parent_key}[{index}]"))
                
            return found_data
        
        # Load Gerber Job File 
        self.logger.debug(f"Parsing Gerber Job File {self.file_path}")
        # Open Gerber Job File (which is in JSON format)
        gbr_job_file = load_json(self.file_path)

        extracted_data = {}
        # Search inside given sections
        for section in sections:
            if section not in gbr_job_file:
                self.logger.warning(f"Section '{section} not found in the Gerber Job File {self.file_path}")
                continue

            self.logger.debug(f"Searching in section: {section}")
            target_section = gbr_job_file[section]
            section_data = search_keywords(data=target_section, keywords=keywords) 

            extracted_data[section] = section_data


        print("Extracted Metadata: ")
        for section, data in extracted_data.items(): 
            print(f"Section: {section}\n")
            for key, value in data.items(): 
                print(f"{key} : {value}")
        
        self.logger.debug("Successfully parsed and extracted relevant Metadata")
        return extracted_data 


class Code_parser: 
    # Parses specific files ()
    def __init__(self):
        pass

    
