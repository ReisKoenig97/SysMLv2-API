import logging 
import re #regex for parsing 
import os
import json

from utils.json_utils import load_json, save_json
from utils.config_utils import load_config

# Libraries CodeParser
import jinja2

# Contains all standardized (for this masters thesis) file parser as a single class for each file format 
# Each class should have methods to read, load, save, and extract metadata 
# NOTE: Some have additional writing to mapping.json due to extending information inside the mapping e.g. index from STEP
# Use 'json_utils' to standardize json file handling such as reading, writing and saving JSON files 

class SysmlParser: 
    """ 
    Parses specific sysml files by getting "metadata" / "@" (abreviation) searching for a specific Structure
    """

    def __init__(self, config=None, sysml_path=None):
        self.logger = logging.getLogger(__name__ + "-SysmlParser")
        #self.logger.debug("Initializing SysmlParser")
        self.config = config
        if self.config is None:
            self.config = load_config(config_file_path="config/default_config.json")
        
        self.sysml_path = sysml_path
        self.sysml_model = None #sysml_model will be extracted from sysml_path
        self.sysml_model = self.load_sysml_model()

    def load_sysml_model(self): 
        """Parses and loads model from self.sysml_path.
        Returns:
            str: The content of the file as a string.
        """
        #self.logger.info(f"SysmlParser - load_sysml_model")
        if not self.sysml_path:
            self.logger.debug(f"No SysML model path provided. Using default path: {os.path.join(self.config['base_se_path'], self.config['base_se_model'])}") 
            self.sysml_path = os.path.join(self.config['base_se_path'], self.config['base_se_model'])
        
        try:
            with open(self.sysml_path, 'r') as file:
                content = file.read()
                #self.logger.debug(f"Successfully loaded sysml model")
            return content
        except Exception as e:
            self.logger.error(f"Failed to load file {self.sysml_path}: {e}")

    def check_metadata_exist(self): 
        """
        Parses the SysML model and extracts metadata definitions and references.
        - Currently used to highlight metadata
        NOTE: 
            current metadata to check:    
                'metadata def test123{ }'
                AND 
                ' metadata test123 about '
        Returns:
            List of of the found metadata definitions names or empty list if not found that structure
        """
        #self.logger.info(f"check_metadata_exist")
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
    
    def get_metadata_about_elements(self, metadata_name = None):
        """ Helper function 
        Extracts all elements with metadata tag '@<metadata_name> about' or 'metadata <metadata_name>

        Parameters: 
            metadata_name : String. Name of the metadata def to search for inside sysml model, if None is provided automatically searches for metadata def 
        """
        #self.logger.info(f"get_metadata_about_elements")

        if not self.sysml_model:
            self.logger.warning("No SysML model loaded. Trying to load model content")
            self.sysml_model = self.load_sysml_model() 

        # NOTE: Currently assumes that we tag whole parts
        # NOTE: later add attribute tags e.g. partA::id
        # 2) Find attributes for each tagged part
        result = {}

        if metadata_name is None: 
            # Find metadata def { ... }
            metadata_def_list = re.findall(r"\bmetadata\s+def\s+(\w+)\s*(?:\{[^}]*\}|;)", self.sysml_model) #\bmetadata\s+def\s+(\w+)\s*\{
            #self.logger.debug(f"No specific metadata_name provided. Automatic search for 'metdata def' found: {metadata_def_list}")
        else:
            metadata_def_list = [metadata_name]

        if not metadata_def_list: 
            # automatic search did not found metadata def structure in sysml model 
            self.logger.warning(f"No metadata definitions found in SysML model.")
            return {}

        all_elements = []
        # Loop through all metadata defs 
        for meta in metadata_def_list:
            if not meta:
                continue  # Falls meta None or empty continue 

            # Search for `@<meta> about partA, partB; patterns 
            metadata_about_pattern = (
                r"@['\"]?" + re.escape(meta) + r"['\"]?\s+about\s*([\w\s,:;\-\.]+?)\s*;"
            )
            matches = re.findall(metadata_about_pattern, self.sysml_model, re.DOTALL)

            elements = []
            if matches:
                elements_raw = matches[0]
                elements = [e.strip().rstrip(';') for e in elements_raw.split(',') if e.strip()]
                elements = [e.split('::')[-1] for e in elements]  # only last element of metadata tag

            if not elements:
                self.logger.debug(f"No matches found for metadata: {meta}")
                continue

            
            #self.logger.debug(f"Found elements for '{meta}': {elements}")
            all_elements.extend(elements)
            #self.logger.debug(f"All elements: {all_elements}")
            

            # Search for attributes for each part inside tagged metadata 
            for path in all_elements:
                #self.logger.debug(f"Current metadata tag: {path}")
                part_pattern = (
                    r"part\s+def\s+" + re.escape(path) + r"\s*\{([^}]*)\}"
                )
                part_match = re.search(part_pattern, self.sysml_model, re.DOTALL)

                attributes = []
                if part_match:
                    #self.logger.debug(f"Current Match: {part_match}")
                    attributes_block = part_match.group(1)

                    # Search for  `attribute name = value; 
                    attr_pattern = r"attribute\s+(\w+)\s*=\s*([^;]+);"
                    attr_matches = re.findall(attr_pattern, attributes_block)

                    for attr_name, attr_value in attr_matches:
                        unit = ""
                        if "[" in attr_value and "]" in attr_value: # Unit detection 
                            unit = attr_value[attr_value.index("[") + 1:attr_value.index("]")]
                            attr_value = attr_value[:attr_value.index("[")].strip()

                        # DataType
                        attr_value = attr_value.strip().strip('"')
                        if attr_value.startswith('"') or attr_value.isalpha():
                            data_type = "string"
                        elif "." in attr_value:
                            data_type = "float"
                        else:
                            data_type = "int" if attr_value.isdigit() else "string"

                        attributes.append({
                            "name": attr_name,
                            "value": attr_value,
                            "unit": unit,
                            "dataType": data_type,
                            "metadata_path": path, # path inside the sysmlv2 model 
                            "metadata_tag": meta # tag = namespace of the metadata def <namespace> aka <meta>
                        })
                        #self.logger.debug(f"Current attributes: {attributes}")
                    
                # Add 'metadata tag' to know from which each tagged element is coming from 
                if meta not in result:
                    result[path] = []
                result[path].extend(attributes)

        #self.logger.debug(f"Extracted metadata: {result}")
        return result
    
    def validate_elementPath(self, elementPath):
        """ 
        Checks if elementPath exists inside sysmlv2 model

        Returns:
            BOOL. True if it exists, else False
        """
        #self.logger.info(f"validate_elementPath")

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
    
    def verify_constraint(self, sysml_file_path, constraint_name):
        """
        Searches SysMLv2 Model for constraint definitions and usages. 
        If a constraint def is found, extract mathematical equation and search for the usage inside the model
        Automatically 

        NOTE: Assumptions for the script to parse and verify constraint
        
        Parameters: 
            constraint_name : String. namespace of constraint def usage 

        Returns:
            Boolean. True if constraint is verified, else false 
        """
        #self.logger.debug(f"verify_constraint")

        # 1) Search sysmlv2 model for constraint def 
        # 2) Search for constraint def usages 
        # 3) Extract relevant information (attributes, parts, ...) for constraint usages 
        # 4) Extract equation from constraint def 
        # 5) Calculate mathematical equation from constraint def 
        # 6) return Bool

        # 1
        constraint_def, constraint_content = self.find_constraint_definitions(sysml_file_path, constraint_name)
        #self.logger.debug(f"Found: {constraint_def}")
        #self.logger.debug(f"With content: {constraint_content}")
        if not constraint_def or not constraint_content:
            self.logger.error(f"No Constraint definition: {constraint_name} found or empty definition")
            return "Could not find provided constraint name or empty constraint definition"
        
        # 2) Search for constraint def usages
        constraint_usage, constraint_usage_content = self.find_constraint_usages(sysml_file_path, constraint_name)
        if not constraint_usage or not constraint_usage_content:
            self.logger.error(f"No usage found for constraint: {constraint_name}")
            return "No usage found for the provided constraint"

        # 3) Extract relevant information from constraint usage
        constraint_usage_info = self.get_constraint_usage_information(constraint_usage_content)
        #self.logger.debug(f"info: {constraint_usage_info}")
        if not constraint_usage_info: 
            self.logger.error(f"No usage information/description found for constraint: {constraint_name}")
            return "No usage information found for the provided constraint"

        # 4) Extract equation as a string
        equation = self.get_constraint_def_equation(constraint_content)
        if not equation:
            self.logger.error(f"Could not extract equation from constraint: {constraint_name}")
            return "Failed to extract equation from constraint definition"
        
        # 5) NOTE: for demonstration only one case will be verified
        # FIXME: For later 
        if "sum(partMasses)" in equation and "<=" in equation: 
            try:
                part_masses = self.get_attribute_value(constraint_usage_info.get("partMasses", []), sysml_file_path=sysml_file_path)
                #self.logger.debug(f"partMasses list: {part_masses}")
                part_masses = sum(part_masses)
                #self.logger.debug(f"partMasses summed up: {part_masses}")
                # Get the numeric value from constraint usage information e.g. "massLimit" : "1000[g]"
                mass_limit_str = constraint_usage_info.get("massLimit", "0[g]")
                mass_limit = float(re.search(r"[-+]?\d*\.?\d+", mass_limit_str).group(0))
                #self.logger.debug(f"MassLimit: {mass_limit}")

                result = part_masses <= mass_limit
                #self.logger.debug(f"Verification result: {result}")

                if result:
                    return f"Constraint ({part_masses} <= {mass_limit}) verified -> ({str(result).upper()})"
                else:
                    return f"Constraint ({part_masses}) <= {mass_limit} violated -> ({str(result).upper()})"
                
            except ValueError as e:
                self.logger.error(f"Error verifying equation: {e}")
                return f"Verification failed: {str(e)}"
            
        # last return is an error
        return "Unsupported equation type"


    def find_constraint_definitions(self, sysml_file_path, constraint_name):
        """
        Searches for 'constraint def' definitions and returns name and body/content inside '{...}'
        
        Parameters:
            sysml_file_path : String. file path, that the user selected 
            constraint_name : String. To search for 
        
        Returns: 
            constraint_name, content inside '{}' if found, else None 
        """
        try:
            with open(sysml_file_path, "r", encoding="utf-8") as file:
                sysml_text = file.read()
        except FileNotFoundError:
            self.logger.error(f"Error (find_constraint_definitions): File '{sysml_file_path}' not found.")
            return None, None

        # Regex für Constraint-Definitionen
        constraint_pattern = r"constraint def (\w+)\s*\{(.*?)\}"
        matches = re.findall(constraint_pattern, sysml_text, re.DOTALL)

        for name, body in matches:
            if name == constraint_name:
                return name, body  # Inhalt zurückgeben, ohne Leerzeichen

        return None, None  # Falls keine passende Constraint gefunden wurde

    def find_constraint_usages(self, sysml_file_path, constraint_name):
        """
        Searches for usages of a given constraint definition inside the SysMLv2 model.
        
        Parameters:
            sysml_file_path : String. Path to the SysMLv2 file.
            constraint_name : String. The name of the constraint definition to search for.

        Returns:
            List of tuples (usage_name, usage_content) if found, else an empty list.
        """
        try:
            with open(sysml_file_path, "r", encoding="utf-8") as file:
                sysml_text = file.read()
        except FileNotFoundError:
            self.logger.error(f"Error (find_constraint_usages): File '{sysml_file_path}' not found.")
            return None, None 

        # Regex for Constraint-Usages (e.g. "constraint massCheck : MassConstraint { ... }")
        usage_pattern = rf"constraint (\w+)\s*:\s*{constraint_name}\s*\{{(.*?)\}}"
        matches = re.findall(usage_pattern, sysml_text, re.DOTALL)

        if not matches:
            self.logger.warning(f"No usages found for constraint: {constraint_name}")
            return None, None 

        usage_name, usage_body = matches[0]
        return usage_name, usage_body

    def get_constraint_usage_information(self, usage_content):
        """
        Dynamically extracts relevant attributes and their assigned values from a constraint usage block.

        Parameters:
            usage_content : String. The content inside a constraint usage block.

        Returns:
            Dictionary with extracted attributes and their values.
        """
        extracted_data = {}

        # Remove unnecessary whitespace and normalize line breaks
        usage_content = usage_content.strip()

        # Split into individual statements based on semicolons, but preserve content across lines
        # Use a regex to handle statements that might span multiple lines
        statements = re.split(r';\s*(?![^\(]*\))', usage_content)  # Split on ; unless inside parentheses

        for statement in statements:
            statement = statement.strip()
            if not statement:  # Skip empty statements
                continue

            # Look for assignments in the form: "in variableName = value"
            match = re.match(r"in\s+(\w+)\s*=\s*(.+)", statement, re.DOTALL)
            if match:
                var_name, var_value = match.groups()
                var_value = var_value.strip()

                # If the value is a list (e.g., (x, y, z)), handle multi-line content
                if var_value.startswith("(") and ")" in var_value:
                    # Extract content inside parentheses
                    list_content = re.search(r'\((.+)\)', var_value, re.DOTALL).group(1)
                    # Split by commas and strip whitespace
                    extracted_data[var_name] = [v.strip() for v in list_content.split(",") if v.strip()]
                else:
                    extracted_data[var_name] = var_value

        return extracted_data if extracted_data else None

    def get_constraint_def_equation(self, constraint_content):
        """
        Parses constraint definition content and searches for equations
        """
        # self.logger.info(f"get_constraint_def_equation)

        # Remove white spaces 
        constraint_content = constraint_content.strip()

        # Simple pattern: Look for a line with a mathematical operator after 'in' declarations
        lines = constraint_content.splitlines()
        for line in lines[::-1]:  # Start from last element due to equation often beeing the last element
            line = line.strip()
            if not line.startswith("in") and any(op in line for op in ["<=", ">=", "<", ">", "=", "!="]):
                #self.logger.debug(f"Extracted equation: {line}")
                return line
        self.logger.warning(f"No equation found in constraint definition content: {constraint_content}")
        return None

    def get_attribute_value(self, attribute_paths : list[str], sysml_file_path : str) -> list[float]: 
        """
        Parses through Sysml model and extracts numeric values for given attribute paths e.g. fc.mass (attribute mass of part FlightController) -> MassValue
        """
        part_name_map = {
        'fc': 'FlightController',
        'cs': 'Chassis',
        'enc': 'Enclosure',
        'motor': 'Motor',
        'prop': 'Propellor',
        'cam': 'Camera',
        'batt': 'Battery',
        'pdb': 'PowerDistributionBoard',
        'esc': 'ElectronicSpeedController',
        'trans': 'Transmitter',
        'rec': 'Receiver',
        'gpsm': 'GPSModule'
        }

        # Multiplicity map
        multiplicity_map = {
            'motor': 4,  # motor[4]
            'prop': 4    # prop[4]
        }

        try:
            # Load Sysml model 
            with open(sysml_file_path, "r", encoding="utf-8") as file:
                sysml_text = file.read()
            
            pattern = r"part def (\w+)\s*\{[^}]*attribute mass\s*=\s*(\d+\.?\d*)\[g\][^}]*\}"
            parts = dict(re.findall(pattern, sysml_text, re.DOTALL))
            #self.logger.debug(f"Extracted parts with mass: {parts}")

            # list for numeric values 
            values = []
            for path in attribute_paths:
                # Check if path is format abbreviation.attribute (e.g. fc.mass)
                if '.' not in path or path.split('.')[-1] != 'mass':
                    self.logger.warning(f"Invalid attribute path: {path}, expected 'part.mass'")
                    values.append(0.0)
                    continue
                    
                # extract abbreviation from path (e.g. "fc" from "fc.mass")
                part_short = path.split('.')[0] # first element 
                part_name = part_name_map.get(part_short) #get full name from part name map 
                if not part_name:
                    self.logger.warning(f"Unknown part short name: {part_short}")
                    values.append(0.0)
                    continue

                # get numeric value
                mass_str = parts.get(part_name, '0')
                mass_value = float(mass_str)

                # if needed, use multiplicity
                multiplicity = multiplicity_map.get(part_short, 1)
                total_mass = mass_value * multiplicity
                values.append(total_mass)
                #self.logger.debug(f"Resolved {path} -> {part_name}.mass = {total_mass}[g]")

            return values

        except FileNotFoundError:
            self.logger.error(f"File not found: {sysml_file_path}")
            return [0.0] * len(attribute_paths)
        except Exception as e:
            self.logger.error(f"Error parsing SysML model: {e}")
            return [0.0] * len(attribute_paths)



class GerberParser:     
    """
    Parses specific files (Gerber X2/3) from the E/E Engineering Domain 
    """
    def __init__(self, gerber_file_path=None): # check string path with and without "." 
        self.logger = logging.getLogger(__name__ + "-GerberParser")
        # Path to gerber file to be parsed
        self.file_path = gerber_file_path

    def get_value(self, elementPath):
        """
        Parses GerberJobFile via given elementPath and returns value 
        Checks if element path is valid 
        NOTE: Helper functions used in metadata manager 
        Returns:
            Value of element from given element path (mapping.json), None if key not found 
        """
        # self.logger.info(f"get_gerber_job_file_value")
        gbr_job_file = load_json(self.file_path)

        keys = elementPath.split(".")  # Split path into individual keys
        current_data = gbr_job_file  # Start from the root of the loaded JSON

        for key in keys:
            self.logger.debug(f"key: {key}")
            # Check if the current key exists in the current level of the JSON data
            if isinstance(current_data, dict) and key in current_data:
                current_data = current_data[key]  # Navigate deeper into the JSON

            else:
                # If the key is not found, log and return None (or raise an exception if needed)
                self.logger.warning(f"Element path '{elementPath}' is invalid: '{key}' not found.")
                return None

        # Return the value if the entire path was found
        # self.logger.info(f"Successfully retrieved value for '{elementPath}': {current_data}")
        return current_data

class CodeParser: 
    """Parses source code that is enriched/annotated with metadata with a specific structure
    NOTE: generates python code with tagged metadata from the sysmlv2 model """
    def __init__(self, code_file_path = None):
        self.logger = logging.getLogger(__name__ + "-CodeParser")
        self.mapping_data = load_json("./config/mapping.json")
        self.code_file_path = code_file_path

    def save_code(self, code, filename="generated_code.py"):
        """ Saves generated code to a file """
        #self.logger.info("save_code")
        
        output_folder = "models/sw_domain"
        filepath = os.path.join(output_folder, filename)

        with open(filepath, "w") as file:
            file.write(code)

        self.logger.info(f"Generated code saved to: {filepath}")

    def get_value(self, elementPath):
        """ 
        Parses code and extracts single value that has been mapped via elementPath in mapping.json
        Checks if element path is valid

        Parameters:
            elementPath (str): The path to the element in the code (e.g., "FlightController.id")
            NOTE: elementPath is generated by software and has to be used by python decorator structure @metadata(..., "elementPath") 

        Returns the value of the elementPath from the mapping.json inside the code and searches for element"""
        #self.logger.info("get_value")
        # 1) Load file 
        # Check if code file path is set
        if not self.code_file_path: 
            self.logger.warning(f"Code file is not provided.")
            return None
        # Check if code file path exist
        if not os.path.exists(self.code_file_path):
            self.logger.error(f"Error: File {self.code_file_path} does not exist")
            raise FileNotFoundError(f"File {self.code_file_path} not found")
        
        # 2) Read and parse file 
        try:
            with open(self.code_file_path, "r") as file:
                code_content = file.readlines() 
        except Exception as e: 
            self.logger.error(f"Error parsing file: {e}")

        # 3) Search for "@metadata(...)"
        # @metadata("max_width", "70", "mm", "int", "PCBDesign", "FlightController.max_width")
        metadata_pattern = re.compile(
            r'@metadata\("([^"]*)",\s*"([^"]*)",\s*"([^"]*)",\s*"([^"]*)",\s*"([^"]*)",\s*"([^"]*)"\)'
        )
        
        # Looping through source code content
        for line in code_content: 
            line = line.strip()
            #self.logger.debug(f"LINE: {line}")
            metadata_match = metadata_pattern.search(line)
            if metadata_match: 
                #self.logger.debug(f"metadata match found: {metadata_match}")
                name, value, unit, dataType, metadata_tag, path = metadata_match.groups()
                #self.logger.debug(f"path: {path}")
                if path == elementPath: 
                    #self.logger.debug(f"Found value: {value}")
                    return value
            
        # 4) Error if we looped through and found nothing
        self.logger.error(f"No value found for given elementPath: {elementPath}")
        raise ValueError(f"No Metadata value found for: {elementPath}")

    def generate_code_from_sysml(self, sysml_file_path: str = None, output_file: str = "generated_code.py"): 
        """ 
        Generates Python code structure from SysMLv2 model using extracted metadata 
        and saves it as a .py source file.

        Parameters:
            sysml_file_path (str): Path to the SysMLv2 model file.
            output_file (str): Name of the output Python file (default: generated_code.py).
        """ 
        #self.logger.debug("generate_code_from_sysml")

        self.sp = SysmlParser(sysml_path=sysml_file_path)
        
        # Extract sysmlv2 metadata
        sysml_metadata = self.sp.get_metadata_about_elements()
        # {  'PCBDesign': [{'name': 'id', 'value': 'abc123', 'unit': '', 'dataType': 'string', 'metadata_path': 'FlightController'}, 
        # {'name': 'name', 'value': 'fc-123', 'unit': '', 'dataType': 'string', 'metadata_path': 'FlightController'}, 
        # ...
        # 'PCB': [{'name': 'id', 'value': 'esc-001', 'unit': '', 'dataType': 'string', 'metadata_path': 'ElectronicSpeedController'}, 
        # {'name': 'name', 'value': 'ESC 30A', 'unit': '', 'dataType': 'string', 'metadata_path': 'ElectronicSpeedController'}, ...}
 

        # Jinja2 Template
        template = jinja2.Template("""
# Generated from SysMLv2 model
from typing import Any

def metadata(name: str, value: Any, unit: str, dataType: str, metadataTag: str = None, elementPath: str = None):
    def wrapper(cls):
        if not hasattr(cls, 'metadata'):
            cls.metadata = []
        cls.metadata.append({
            "name": name,
            "value": value,
            "unit": unit,
            "dataType": dataType,
            "metadata_tag": metadataTag,
            "elementPath": elementPath or f"{cls.__name__}.{name}",
        })
        return cls
    return wrapper

{% for element_name, attribute_list in sysml_metadata.items() %}
{% for attribute in attribute_list -%}
@metadata("{{ attribute.name }}", "{{ attribute.value }}", "{{ attribute.unit }}", "{{ attribute.dataType }}", "{{ attribute.metadata_tag }}", "{{ attribute.metadata_path }}.{{ attribute.name }}")
{% endfor %}
class {{ element_name }}:
    def __init__(self, **kwargs):
        {% for attribute in attribute_list -%}
        self.{{ attribute.name }} = "{{ attribute.value }}"
        {% endfor %}

{% endfor %}
""")

        # Generate Python-Code from template 
        generated_code = template.render(sysml_metadata=sysml_metadata)

        # Save generated code 
        output_dir = "models/sw_domain"
        os.makedirs(output_dir, exist_ok=True)  # In case folder does not exist -> create folder 
        output_path = os.path.join(output_dir, output_file)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(generated_code)

        #self.logger.info(f"Python source code generated and saved to: {output_path}")
        return generated_code
        
class StepParser:
    """A parser for STEP files (STEP AP242) used in Mechanical Engineering."""

    def __init__(self, step_file_path=None):
        """
        Initialize the StepParser with a file path.

        Parameters:
            step_file_path (str, optional): Path to the STEP file. Defaults to None.
        """
        self.logger = logging.getLogger(__name__ + "-StepParser")
        self.step_file_path = step_file_path
        self.step_file_content = None #self.load_step_file(step_file_path=self.step_file_path)

    def load_step_file(self, step_file_path=None):
        """
        Load the content of a STEP file.

        NOTE:
            - STEP files lack a predefined metadata structure (unlike JSON or XML). 
            - Metadata must be extracted from the raw content using reading and regex if needed.

        Parameters:
            filepath (str, optional): Path to the STEP file. Defaults to None.

        Returns:
            str: File content as a string, or an empty string ("") if loading fails.
        """
        #self.logger.info("load_step_file")
        if not step_file_path:
            self.logger.warning("No file path provided. Returning ''")
            return ""

        try:
            with open(step_file_path, 'r') as file:
                content = file.read()
                # Set loaded step file content to content
                self.step_file_content = content
                #self.logger.debug("STEP file loaded successfully")
                return content
        except Exception as e:
            self.logger.error(f"Failed to load STEP file '{step_file_path}': {e}")
            return ""
   
    def get_value(self, elementPath):
        """
        Extracts a value from the STEP file based on the given elementPath.
        It also keeps track of the index position for later updates.
        Writes "index" parameter inside mapping.json 
        
        Parameters:
            elementPath (str): The STEP path to search for (e.g., "DATA.#11458=CARTESIAN_POINT" or "FILE_NAME").
            
        Returns:
            str | None: The extracted value, or None if not found.
        """
        #self.logger.info(f"get_value")

        # Load step file content
        self.step_file_content = self.load_step_file(step_file_path=self.step_file_path)

        # Differentiate between HEADER data and DATA section
        if elementPath.startswith("DATA."):
            # Extract the numeric index from the elementPath (e.g., #11458)
            match = re.search(r"#(\d+)", elementPath)
            if not match:
                self.logger.error(f"Invalid elementPath format: {elementPath}")
                return None

            element_id = match.group(0)  # Example: "#11458"

            # Search for the line in the STEP file containing the element
            pattern = rf"{element_id}\s*=\s*([\w_]+)\((.*?)\);"
            match = re.search(pattern, self.step_file_content, re.DOTALL) # DOTALL allows multiline matches
            #self.logger.debug(f"Match for '{element_id}': {match}")

            if not match:
                self.logger.warning(f"Element '{element_id}' not found in the STEP file.")
                return None

            element_type = match.group(1) # e.g. "NEXT_ASSEMBLY_USAGE_OCCURRENCE"
            element_data = match.group(2) # value inside the brackets. e.g. (#58,#116) -> "#58,#116"
            
            # Split each element inside the element_data / brackets (e.g., #58,#116)
            # re.sub Removes single or double quotes from the values
            values = [re.sub(r"^['\"]|['\"]$", "", i.strip()) for i in element_data.split(",")]
            #self.logger.debug(f"Extracted values: {values}")

            # Load mapping.json to update the index for the current element
            mapping = load_json("config/mapping.json")
            index = 0 

            for element in mapping["STEP"]:
                if element.get("index") != "":
                    index = int(element["index"])
                    element["value"] = values[index]  # Update value from STEP file
                    break
                else:
                    for idx, value in enumerate(values):
                        if value == element["value"]:
                            element["index"] = str(idx)
                            save_json("config/mapping.json", mapping)
                            index = idx
                            break
                    else:
                        continue
                    break
            return values[index] 
        
        # Handle HEADER section (e.g., "FILE_NAME.name")
        else:
            # Validate element_path format (e.g., "SECTION.ATTRIBUTE")
            keys = elementPath.split(".")
            if len(keys) != 2:
                self.logger.error("Invalid elementPath format. Expected: 'SECTION.ATTRIBUTE'")
                return None

            section_name, attribute = keys

            # Search for the section in the STEP file (e.g., FILE_NAME(...);)
            section_pattern = rf"{section_name}\((.*?)\);"
            section_match = re.search(section_pattern, self.step_file_content, re.DOTALL)  # DOTALL allows multiline matches

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

                    # Extract value enclosed in single or double quotes (e.g., "'Agri_UAV2'" -> "Agri_UAV2")
                    match = re.search(r"'(.*?)'|\"(.*?)\"", raw_value)
                    clean_value = match.group(1) if match else raw_value

                    return clean_value
                else:
                    self.logger.warning(f"Index {index} out of range for section '{section_name}'.")
                    return None
            else:
                self.logger.warning(f"Attribute '{attribute}' not found in section '{section_name}'.")
                return None
             