import logging 
from utils.json_utils import save_json, load_json
import os 
from datetime import datetime
import uuid 

class MetadataManager:
    """
    Class to manage metadata between domain models and SysMLv2
    Writes, extracts and maps data inside a mapping.json
    Creates UUIDS for each mapped element
    """
    def __init__(self, config):
        """
        Initializes the metadata manager
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initialized MetadataManager")
        
        self.config = config
        self.mapping_template_file_path = "./config/mapping_template.json"
        self.mapping_file_path = "./config/mapping.json"
        # Parameters will be set later by functions  
        self.sysml_model = None
        self.domain_model = None 

        #Create mapping_template automatically, if not already existing 
        self.create_mapping_from_template() 

    def create_mapping_from_template(self):
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
            "elementPath" : sysml_element_path,
            "filePath" : sysml_path, 
            "created" : timestamp,
            "lastModified" : timestamp
        }

        domain_element = {
            "uuid" : uuid_domain_element,
            "name" : domain_element_path.split(".")[-1], #last element from element path 
            "value" : domain_element_value,
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