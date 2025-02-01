import logging 
import os 
import uuid 
import re # Regex 

from utils.json_utils import save_json, load_json
from datetime import datetime
from versioncontrol import VersionControl
from file_parser import SysmlParser

class MetadataManager:
    """
    Class to manage metadata between domain models and SysMLv2
    Writes, extracts and maps data inside a mapping.json
    Creates UUIDS for each mapped element
    Responsible for versioning, commits and traceability 
    """
    def __init__(self, config, versioncontrol=None):
        """
        Initializes the metadata manager
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized MetadataManager")
        
        self.config = config
        self.mapping_template_file_path = "./config/mapping_template.json"
        self.mapping_file_path = "./config/mapping.json"
        self.repo_path = self.config["repo_path"]
        self.vc = versioncontrol
        # Parameters will be set later by functions  
        self.sysml_model = None
        self.domain_model = None
        # List of keywords for regex search inside the sysml file 
        self.keywords = ["part", "part def", "package", "attribute"]
        self.keywords_pattern = "|".join(self.keywords)
        self.datatypes = ["Real", "Integer", "String", "Boolean", "Enumeration"]

        #Create mapping_template automatically, if not already existing 
        self.create_mapping_file_from_template()
        self.logger.debug("MetadataManager initialized")

    def create_mapping_file_from_template(self):
        """Creates empty mapping.json template"""
        self.logger.debug(f"Creating mapping.json from template")

        #Check if 'mapping.json' exist 
        if os.path.exists(self.mapping_file_path): 
            self.logger.info(f"Mapping file already exists at {self.mapping_file_path}")
            return
        
        # Load Template and save 'mapping.json' from template 
        template = load_json(file_path=self.mapping_template_file_path) 
        save_json(file_path=self.mapping_file_path, data=template)

    def map_metadata(self, sysml_path, sysml_element_path, sysml_element_value, domain_file_format, domain_path, domain_element_path, domain_element_value): 
        """
        Links/Maos metadata from domain models with SysMLv2 data that the user selected inside the GUI 
        Creates UUIDs for the mapped elements, validates paths, and updates the mapping.json.

        Parameters: 
            sysml_path : object entry widget. File path to the directory that contains the sysmlv2 file 
            sysml_element_path : object entry widget. Specific path to the element. e.g. package.partA.len
            sysml_element_value : object entry widget. Value of the sysml element
            domain_file_foramt : object entry widget. File Format of specific domain e.g. GerberJobFile or STEP 
            domain_path : object entry widget File path to the directory that contains the sysmlv2 file 
            domain_element_path : object entry widget. Specific path to the element e.g. "GeneralSpecs.Size.X"
            domain_element_value : object entry widget. Value of domain element 
        """
        self.logger.debug(f"Mapping Metadata: SysMLv2: {sysml_element_path} <---> Domain: {domain_element_path}")

        

        # Validate file existence
        if not os.path.exists(sysml_path):
            self.logger.error(f"SysMLv2 file does not exist: {sysml_path}")
            raise FileNotFoundError(f"SysMLv2 file does not exist: {sysml_path}")
        if not os.path.exists(domain_path):
            self.logger.error(f"Domain file does not exist: {domain_path}")
            raise FileNotFoundError(f"Domain file does not exist: {domain_path}")
        
        # Generate UUIDs for each element
        uuid_sysml_element = str(uuid.uuid4())
        uuid_domain_element = str(uuid.uuid4())
        self.logger.debug(f"Generated UUIDs: SysMLv2: {uuid_sysml_element}, Domain: {uuid_domain_element}")

        # Create timestamp
        timestamp = datetime.now().strftime("%d.%m.%Y")

        sysml_element = {
            "uuid" : uuid_sysml_element,
            "name" : sysml_element_path.split(".")[-1], #last element from element path 
            "value" : sysml_element_value,
            "unit" : "", 
            "dataType" : "",
            "elementPath" : sysml_element_path,
            "filePath" : sysml_path, 
            "created" : timestamp,
            "lastModified" : timestamp
        }

        domain_element = {
            "uuid" : uuid_domain_element,
            "name" : domain_element_path.split(".")[-1], #last element from element path 
            "value" : domain_element_value,
            "unit" : "", 
            "dataType" : "",
            "elementPath" : domain_element_path,
            "filePath" : domain_path, 
            "created" : timestamp,
            "lastModified" : timestamp  
        }

        new_mapping = {
            "sourceUUID" : uuid_domain_element,
            "targetUUID" : uuid_sysml_element,
            "created" : timestamp
        }
        
        self.logger.debug(f"Loading mapping.json and add new mapping")
        # Load existing mapping.json to extend with data 
        mapping = load_json(file_path=self.mapping_file_path)

        # Ensure the domain file format exists in the mapping
        if domain_file_format not in mapping:
            self.logger.info(f"{domain_file_format} section not found in mapping.json. Creating new section.")
            mapping[domain_file_format] = []

        # TODO: Check DataTypes 

        # Append elements to sysmlv2
        mapping["SysMLv2"].append(sysml_element)
        mapping[f"{domain_file_format}"].append(domain_element)
        mapping["Mappings"].append(new_mapping)

        # Save updated mapping.json
        if save_json(file_path=self.mapping_file_path, data=mapping):
            self.logger.debug(f"Mapping successfully saved at: {self.mapping_file_path}")
            return True
        else: 
            return False 
        
    def update_sysml_model(self):
        """
        Updates/changes sysml model with domain metadata that has been mapped via mapping.json 
        Overwrites mapped element values (also checks if new values are set from domain files)
        """
        self.logger.info(f"Startig update_sysml_model")
        # 1) Load mapping.json 
        mapping = load_json(file_path=self.mapping_file_path)

        # 2) Loop through all mappings and update SysMLv2 model with domain metadata
        # Overwrite values of mapped elements in "SysMLv2" with values from "GerberJobFile" etc."
        for mapping_entry in mapping["Mappings"]:
            source_uuid = mapping_entry["sourceUUID"]
            target_uuid = mapping_entry["targetUUID"]
            #self.logger.debug(f"Mapping: {source_uuid} --> {target_uuid}")

            # Find source and target elements
            source_element = next(
                (elem for elem in mapping["GerberJobFile"] if elem["uuid"] == source_uuid), None)
            target_element = next(
                (elem for elem in mapping["SysMLv2"] if elem["uuid"] == target_uuid), None)
            #self.logger.debug(f"Source element: {source_element}")
            #self.logger.debug(f"Target element: {target_element}")

            # Check if both elements were found
            if source_element is None or target_element is None:
                self.logger.error(f"Source or target element not found in mapping.json: {source_uuid}, {target_uuid}")
                continue

            # Open Sysml file based on given filePath for each element inside "SysMLv2" and check file existent
            target_file_path = os.path.join(self.repo_path, target_element["filePath"])
            #self.logger.debug(f"Opening SysMLv2 file with target file path: {target_file_path}")
            if not os.path.exists(target_file_path):
                self.logger.error(f"SysMLv2 file does not exist: {target_file_path}")
                continue

            # Read sysml file and update the content
            with open(target_file_path, "r") as file:
                sysml_content = file.readlines() #returns list of string lines 
 
            updated_content = self.update_value_in_sysml_model(sysml_content, target_element['elementPath'], source_element['value'], source_element['unit'])
            self.logger.debug(f"Updated content: {updated_content}")
            # Write updated content back to file
            with open(target_file_path, "w") as file:
                file.writelines(updated_content)

            # Update target element value with source element value
            # target_element["value"] = source_element["value"]
            # # Add timestamp for last modified
            # target_element["lastModified"] = datetime.now().strftime("%d.%m.%Y")

        #self.logger.debug(f"Sucecssfully updated SysMLv2 model with domain metadata") 
        
    def update_value_in_sysml_model(self, content, element_path, source_value, unit=""): 
        """
        Helper Function
        Updates the value of the target element in the SysMLv2 file content with the source value from the domain model file
        
        Parameters:
            content : list of strings. Content of the SysMLv2 file
            element_path : str. Path to the target element in the SysMLv2 file
            source_value : str. Value of the source element from the domain model file 
        """
        self.logger.debug(f"Updating value in SysMLv2 model: {element_path} with value: {source_value}")
        element_path_splitted = element_path.split(".")
        #self.logger.debug(f"Element path splitted: {element_path_splitted} with length: {len(element_path_splitted)}")
        depth = 0
        in_target_block = False
        updated_content = []
        is_number = False

        # Check data type of source value (and convert to  number float if possible)
        try:
            source_value = float(source_value)
            is_number = True
        except ValueError:
            source_value = f'"{source_value}"'

        for line in content:
            stripped_line = line.strip()
            #self.logger.debug(f"Depth: {depth}. Current Line: {stripped_line}")
            match = None
            # Navigate to the target element
            if depth < len(element_path_splitted): 
                if re.match(rf"^\s*({self.keywords_pattern})\s+{re.escape(element_path_splitted[depth])}\s*\{{?", stripped_line):
                    #self.logger.info(f"Match found for element path: {element_path_splitted[depth]}")
                    depth += 1

                    if depth == (len(element_path_splitted)-1):
                        in_target_block = True
                        #self.logger.debug(f"In target block TRUE")
                    
                if in_target_block: 
                    #self.logger.debug(f"Inside Targetblock")
                    #match = re.match(r"^\s*attribute\s+(\w+)\s*(:|=)\s*(\w+)\s*(;|\s+)", stripped_line)
                    match = re.search(r"^\s*attribute\s+(\w+)\s*(:|=)\s*(\w+|\S+)\s*(;|\s+)", stripped_line)
                    if match:
                        depth = (len(element_path_splitted)-1)  # we are at the last element of given path 
                        attribute_name = match.group(1)
                        operator = "=" if match.group(2) == ":" else match.group(2)
                        unit_target_value = f"[{unit}]" if is_number and len(unit)>0 else "" 
                        #current_value = match.group(3)
                        semicolon = match.group(4) or ""    

                        if attribute_name == element_path_splitted[-1]:
                            indentation = " " * (depth * 4)
                            # Replace value of the target element with source value (mapped domain model value)
                            updated_line = f"{indentation}attribute {attribute_name} {operator} {source_value}{unit_target_value}{semicolon}\n"
                            #self.logger.debug(f"Updating line to: {updated_line.strip()}")
                            updated_content.append(updated_line)
                            in_target_block = False  # Exit target block after updating value
                        else:
                            updated_content.append(line)
                    else: 
                        updated_content.append(line)
                else: 
                    updated_content.append(line)
            else:
                updated_content.append(line)
        return updated_content
