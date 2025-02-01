import logging 
import re #regex for parsing 
import os

from utils.json_utils import load_json
from utils.config_utils import load_config


# Contains all standardized (for this masters thesis) file parser as a single class for each file format 
# Each class should have methods to read, load, save, and extract metadata
# Use 'json_utils' to standardize json file handling such as reading, writing and saving JSON files 

class SysmlParser: 
    """ Parses specific sysml files by getting "metadata" / "@" (abreviation)
    searching for a specific Structure
    
    DEMONSTRATION 
        To identify if the sysml file has a metadata that the script can parse: 
        1) Metadata def with or without content
            metadata def <name> { ... }
            metadata def <name>; 
        
        2) About paths to tag certain elements of the model
            metadata<name> about 
            @<name> about
        NOTE: 
            - Inside each line of about paths there can't be any comments after ';'
    """

    def __init__(self, config=None, sysml_path=None):
        self.logger = logging.getLogger(__name__)
        #self.logger.debug("Initializing SysmlParser")
        self.config = config
        if self.config is None:
            self.config = load_config(config_file_path="config/default_config.json")
        
        self.sysml_path = sysml_path
        self.sysml_model = None #sysml_model will be extracted from sysml_path
        self.logger.debug(f"SysmlParser initialized")

    def load_sysml_model(self): 
        """Parses and loads model from self.sysml_path.
        Returns:
            str: The content of the file as a string.
        """
        if not self.sysml_path:
            self.logger.debug(f"No SysML model path provided. Using default path: {os.path.join(self.config['base_se_path'], self.config['base_se_model'])}") 
            self.sysml_path = os.path.join(self.config['base_se_path'], self.config['base_se_model'])
        
        try:
            with open(self.sysml_path, 'r') as file:
                content = file.read()
                self.logger.debug(f"Successfully loaded sysml model")
            return content
        except Exception as e:
            self.logger.error(f"Failed to load file {self.sysml_path}: {e}")

    def check_metadata_exist(self): 
        # TODO: REDO this helper function 
        """Parses the SysML model and extracts metadata definitions and references.
        
        NOTE: 
            current metadata to check:    
                'metadata def test123{ }'
                AND 
                ' metadata test123 about '
        Returns:
            List of of the found metadata definitions names or empty list if not found that structure
        """
        self.logger.debug(f"Checking for certain metadata structure inside sysml model")
        self.sysml_model = self.load_sysml_model() 
        # 1 Check if sysml model can be loaded from initialized class sysml model path 
        if not self.sysml_model:
            self.logger.warning("No SysML model loaded.")
            return  
        # DEBUG 
        first_few_lines = "\n".join(self.sysml_model.splitlines()[:15]) # Only shows :x lines inside the app.log 
        self.logger.debug(f"Given SysML model: {first_few_lines}")

        # Regex for 'metadata def <name>' and 'metadata def <name>{...}'
        #metadata_def_pattern = r'metadata\s+def\s+(\w+)\s*(?=\s*(\{|\s*;))'
        # ['\"] includes optinal ' or " for the name 
        metadata_def_pattern = r"metadata\s+def\s+['\"]?(\w+)['\"]?\s*(?=\{)"

        #metadata_def_pattern = r'metadata\s+def\s+(\w+)\s*(\{*.?\})?' # . represent any character 
        metadata_def_matches = re.findall(metadata_def_pattern, self.sysml_model, re.DOTALL) #re.DOTALL includes line breaks

        # Regex for '@<name> about' or 'metadata <name> about'
        metadata_about_pattern = r"@(\w)\s+|metadata\s+(\w)['\"]?\s+about"
        metadata_about_matches = re.findall(metadata_about_pattern, self.sysml_model, re.DOTALL)

        self.logger.debug(f"metadata def matches: {metadata_def_matches}")
        # Extract only the metadata names from the match results
        metadata_names = [match for match in metadata_def_matches]

        self.logger.debug(f"'Metadata def' names: {metadata_names}")
        #self.logger.debug(f"'Metadata about' matches: {metadata_about_matches}")

        # Return list containing found metadata def names 
        # OPTIONAL: Include about matches for the content 
        return metadata_names
    
    def get_metadata_about_elements(self, metadata_name):
        """ Helper function 
        Extracts all elements with metadata tag '@<name> about' or 'metadata <name>

        Parameters: 
            medata_name : String. Name of the metadata def to search for inside sysml model  
        """
        if not self.sysml_model:
            self.logger.warning("No SysML model loaded.")
            return 

        # Flexible regex to handle multi-line and complex formats e.g. packageA::partDefs::partA, ... 
        #metadata_about_pattern = r'@' + re.escape(metadata_name) + r'\s+about\s+([\w\:\-\.]+(?:\s*,\s*[\w\:\-\.]+)*\s*);'
        metadata_about_pattern = (
        r"@['\"]?" + re.escape(metadata_name) + r"['\"]?\s+about\s+"
        r"([\w\:\-\.]+(?:\s*,\s*[\w\:\-\.]+)*\s*);"
        )

        matches = re.findall(metadata_about_pattern, self.sysml_model, re.DOTALL)

        # If matches were found, split them and return as a list
        if matches:
            elements = matches[0].split(',')  # Split elements separated by commas
            # return [e.strip() for e in elements]  # Remove unnecessary spaces
            # OPTIONAL
            # For each element, split by ':' and take the last part
            # e.g. 'packageA::partDefinitions::partB' -> extracts 'partB'  
            processed_elements = [e.strip().split(':')[-1] for e in elements]
            return processed_elements
        return []
    
    def validate_element_path(self, element_path):
        self.logger.debug(f"Validating element path: {element_path}")

        if not self.sysml_model:
            self.logger.warning("SysML model is None! Attempting to load model.")
            self.sysml_model = self.load_sysml_model()

        path_splitted = element_path.split('.')
        self.logger.debug(f"Derived path: {path_splitted}")
        valid_keywords = ["part def", "part", "attribute", "package"]

        try:
            #self.logger.debug(f"Opening SysMLv2 file with path: {self.sysml_path}")
            with open(self.sysml_path, 'r') as sysml_file:
                content = sysml_file.read()
                # content = self.remove_comments(content)  # Remove comments for cleaner parsing
        except FileNotFoundError:
            self.logger.error(f"SysMLv2 File not found: {self.sysml_path}")
            raise

        # Initialize current content and expected depth
        current_content = content
        expected_depth = 0

        for index, partial_path in enumerate(path_splitted):
            # Match the current element with valid keywords at the current depth
            match = re.search(rf'({"|".join(valid_keywords)})\s+{re.escape(partial_path)}(\s*:\s*\w+)?\b', current_content)
            #self.logger.debug(f"Current Match for '{partial_path}' at depth {expected_depth}: {match}")
            
            if not match:
                self.logger.warning(f"Keyword '{partial_path}' not found or not preceded by valid keyword.")
                return False

            # Get remaining content after the current match
            remaining_content = current_content[match.end():]
            #self.logger.debug(f"Remaining content after '{partial_path}': {remaining_content}")

            # Check if it's the last element and ensure we're not expecting further depth
            if index == len(path_splitted) - 1:
                # Final element must not expect further depth
                # NOTE: We assume that the final element is an attribute or a semicolon
                if "attribute" in match.group(1) or ";" in remaining_content:
                    self.logger.debug(f"Final element '{partial_path}' is valid.")
                    return True
                else:
                    self.logger.warning(f"Invalid final element structure for '{partial_path}'.")
                    return False

            # Look for opening to go one level deeper
            open_brace_index = remaining_content.find('{')

            if open_brace_index != -1:
                #self.logger.debug(f"Entering deeper level after '{partial_path}'.")
                expected_depth += 1
                current_content = remaining_content[open_brace_index + 1:]
            else:
                # If neither an opening nor a closing brace is found, the structure is invalid
                self.logger.warning(f"Invalid structure: No valid braces after '{partial_path}'.")
                return False

        self.logger.debug(f"Path '{element_path}' is valid in SysMLv2 model.")
        return True


class GerberParser:    
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

    
