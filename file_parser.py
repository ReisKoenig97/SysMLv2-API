import logging 
import re #regex for parsing 
import os
import json

from utils.json_utils import load_json
from utils.config_utils import load_config

from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.TopAbs import TopAbs_COMPOUND, TopAbs_COMPSOLID, TopAbs_SOLID, TopAbs_SHELL, TopAbs_FACE, TopAbs_WIRE, TopAbs_EDGE, TopAbs_VERTEX
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TopExp import TopExp_Explorer

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
        self.logger.info(f"SysmlParser initialized")

    def load_sysml_model(self): 
        """Parses and loads model from self.sysml_path.
        Returns:
            str: The content of the file as a string.
        """
        self.logger.info(f"SysmlParser - load_sysml_model")
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
        self.logger.info(f"SysmlParser - check_metadata_exist")
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
        self.logger.info(f"SysmlParser - get_metadata_about_elements")
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
    
    def validate_elementPath(self, elementPath):
        self.logger.info(f"SysmlParser - validate_elementPath")

        if not self.sysml_model:
            self.logger.warning("SysML model is None! Attempting to load model.")
            self.sysml_model = self.load_sysml_model()

        path_splitted = elementPath.split('.')
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

        self.logger.debug(f"Path '{elementPath}' is valid in SysMLv2 model.")
        return True

class GerberParser:    
    # Parses specific files (Gerber X2/3) from the E/E Engineering Domain 
    """
    TODO: 
    1) Read gerber file 
    2) Parse through and extract metadata 
    3) Save Metadata in JSON Formatted file 
    """
    def __init__(self, file_path="models/ee_domain/Hades_project-job.gbrjob"): # check string path with and without "." 
        self.logger = logging.getLogger(__name__)

        # Contains extracted informations of parsed gerber file 
        #self.data = {}
        # Path to gerber file to be parsed
        self.file_path = file_path
        self.logger.info(f"GerberParser initialized")

    def get_value(self, elementPath):
        """
        Parses GerberJobFile via given elementPath and returns value 
        Checks if element path is valid 
        NOTE: Helper functions used in metadata manager 
        Returns:
            Value of element from given element path (mapping.json), None if key not found 
        """
        self.logger.info(f"GerberParser - get_gerber_job_file_value")
        # Load the Gerber job file using the load_json function
        try: 
            with open(self.file_path, "r", encoding="utf-8") as f: 
                gbr_job_file = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load Gerber job file")

        keys = elementPath.split(".")  # Split path into individual keys
        current_data = gbr_job_file  # Start from the root of the loaded JSON

        for key in keys:
            # Check if the current key exists in the current level of the JSON data
            if isinstance(current_data, dict) and key in current_data:
                current_data = current_data[key]  # Navigate deeper into the JSON
            else:
                # If the key is not found, log and return None (or raise an exception if needed)
                self.logger.warning(f"Element path '{elementPath}' is invalid: '{key}' not found.")
                return None

        # Return the value if the entire path was found
        self.logger.info(f"Successfully retrieved value for '{elementPath}': {current_data}")
        return current_data

class Code_parser: 
    # Parses specific files ()
    def __init__(self):
        pass

class StepParser: 
    """ Parses specific STEP files (STEP AP242) from the Mechanical Engineering Domain """

    def __init__(self, step_file_path = None):
        self.logger = logging.getLogger(__name__)

        self.step_file_path = step_file_path
        self.step_file_content = self.load_step_file()
        self.step_reader = STEPControl_Reader()
        self.logger.info(f"StepParser initialized")
        
    def load_step_file(self):
        """ 
        Load Step file content
        NOTE: 
            - Step Files don't have a specific metadata structure like JSON or XML files
            - Therefore, we need to extract metadata from the file content itself via read and regex search 
        
        Returns:
            str: The content of the file as a string or empty ("") if file not found
        """
        self.logger.info(f"StepParser - load_step_file")
        try: 
            with open(self.step_file_path, 'r') as file: 
                step_data = file.read()
                self.logger.debug(f"Successfully loaded STEP file")
                return step_data
        except ExceptionGroup as e:                      
            self.logger.error(f"Failed to load file {self.step_file_path}: {e}")
            return ""
        
    def extract_metadata(self):
        """ 
        Extracts metadata from the STEP file
        
        Returns:
            dict: Metadata extracted from the STEP file
        """
        self.logger.info(f"StepParser - extract_metadata")
        # return metadata as a dictionary
        metadata = {}

        # Extract metadata from the STEP file via regex search
        # Metadata: Product Name
        product_name_match = re.search(r'PRODUCT\(\s*\'(.*?)\'', self.step_file_content)
        metadata["product_name"] = product_name_match.group(1) if product_name_match else "None"

        return metadata
    
    def extract_shapes(self):
        """
        Load and analyze the STEP file to detect shapes.
        Returns:
            List of tuples containing the shape type and the shape itself.
        """
        self.logger.info(f"StepParser - extract_shapes")
        status = self.step_reader.ReadFile(self.step_file_path)
        if status != IFSelect_RetDone:
            self.logger.error("Error: File can not be loaded!")
            return []
        
        self.step_reader.TransferRoots()
        shape = self.step_reader.OneShape()
        return self.get_shapes(shape)
    
    def get_shapes(self, shape):
        """Returns a list with all shapes in the given object (step)"""
        shape_types = [TopAbs_COMPOUND, TopAbs_COMPSOLID, TopAbs_SOLID, TopAbs_SHELL, TopAbs_FACE, TopAbs_WIRE, TopAbs_EDGE, TopAbs_VERTEX]
        #shape_names = ["COMPOUND", "COMPSOLID", "SOLID", "SHELL", "FACE", "WIRE", "EDGE", "VERTEX"]
        shape_names = ["COMPOUND", "COMPSOLID", "SOLID"]
        
        detected_shapes = []
        
        for shape_type, name in zip(shape_types, shape_names):
            explorer = TopExp_Explorer(shape, shape_type)
            while explorer.More():
                detected_shapes.append((name, explorer.Current()))
                explorer.Next()
        
        return detected_shapes
    
    def get_value(self, elementPath):
        """
        Extracts a specific value from a STEP file based on the given element path.

        The function searches for the specified section (e.g., FILE_NAME, FILE_DESCRIPTION) 
        and retrieves the requested attribute value. Attribute positions are mapped using 
        a predefined index table.

        Parameters:
            elementPath (str): The path to the desired element in the format "SECTION.ATTRIBUTE".
                                Example: "FILE_NAME.name" or "FILE_DESCRIPTION.description".

        Returns:
            str | None: The extracted value as a string, or None if the element is not found.
        """
        self.logger.info("StepParser - get_value")

        # Read the STEP file
        try:
            with open(self.step_file_path, "r", encoding="utf-8") as f:
                step_file_content = f.read()
        except Exception as e:
            self.logger.error(f"Failed to load STEP file: {e}")
            return None

        # Validate the format of elementPath
        keys = elementPath.split(".")
        if len(keys) != 2:
            self.logger.error("Invalid elementPath format. Expected: 'SECTION.ATTRIBUTE'")
            return None

        section_name, attribute = keys

        # Search for the section in the STEP file (e.g., FILE_NAME(...);)
        section_pattern = rf"{section_name}\((.*?)\);"
        section_match = re.search(section_pattern, step_file_content, re.DOTALL)  # DOTALL allows multiline matches

        if not section_match:
            self.logger.warning(f"Section '{section_name}' not found in the STEP file.")
            return None

        section_content = section_match.group(1)
        values = [value.strip() for value in section_content.split(",")]

        # Define attribute position mappings for known sections
        metadata = {
            "FILE_NAME": {
                "name": 0,
                "time_stamp": 1,
                "author": 2,
                "organization": 3,
                "preprocessor_version": 4,
                "originating_system": 5,
                "authorization": 6
            },
            "FILE_DESCRIPTION": {
                "description": 0,
                "implementation_level": 1
            }
        }

        # Retrieve the value based on the attribute position
        if section_name in metadata and attribute in metadata[section_name]:
            index = metadata[section_name][attribute]

            if index < len(values):  # Ensure index is within range
                raw_value = values[index]  # Example: /* name */ 'Agri_UAV2'

                # Extract value enclosed in single or double quotes
                match = re.search(r"'(.*?)'|\"(.*?)\"", raw_value)
                clean_value = match.group(1) if match else raw_value

                return clean_value
            else:
                self.logger.warning(f"Index {index} out of range for section '{section_name}'.")
                return None
        else:
            self.logger.warning(f"Attribute '{attribute}' not found in section '{section_name}'.")
            return None