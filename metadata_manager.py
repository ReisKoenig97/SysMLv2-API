import logging 
import os 
import uuid 
import re # Regex 
from tkinter import messagebox

from utils.json_utils import save_json, load_json
from datetime import datetime

class MetadataManager:
    """
    Class to manage metadata between domain models and SysMLv2
    Writes, extracts and maps data inside a mapping.json
    Creates UUIDS for each mapped element inside mapping.json 
    Responsible for versioning, commits and traceability 
    """
    def __init__(self, config, versioncontrol=None, gerberparser=None, stepparser=None, codeparser=None, sysmlparser=None):
        self.logger = logging.getLogger(__name__ + "-MetadataManager")
        #self.logger.info(f"Initialized MetadataManager")
        
        self.config = config
        self.mapping_template_file_path = "./config/mapping_template.json"
        self.mapping_file_path = "./config/mapping.json"
        # NOTE: not only dependend on repo path inside config.json also dependend on which OS the mapping has been made
        self.repo_path = self.config["repo_path"] # Change it between windows and macOS 
        self.vc = versioncontrol
        self.fp_gerber = gerberparser
        self.fp_step = stepparser 
        self.fp_code = codeparser
        self.fp_sysml = sysmlparser
        
        # Parameters will be set later by functions 
        self.sysml_model = None
        self.domain_model = None
        # List of keywords for regex search inside the sysml file 
        self.keywords = ["part", "part def", "package", "attribute"]
        self.keywords_pattern = "|".join(self.keywords)
        self.datatypes = ["Real", "Integer", "String", "Boolean", "Enumeration"]

        #Create mapping_template automatically, if not already existing 
        self.create_mapping_file_from_template()
        #self.logger.info("MetadataManager initialized")

    def create_mapping_file_from_template(self):
        """Creates empty mapping.json template"""
        #self.logger.info(f"create_mapping_file_from_template") 
        #Check if 'mapping.json' exist 
        if not os.path.exists(self.mapping_file_path): 
            # Load Template and save 'mapping.json' from template 
            template = load_json(file_path=self.mapping_template_file_path) 
            save_json(file_path=self.mapping_file_path, data=template)
        else:
            #self.logger.info(f"Mapping file already exists at {self.mapping_file_path}")
            return 
        
    def map_metadata(self, sysml_path, sysml_element_path, sysml_element_value, sysml_element_unit, domain_file_format, domain_path, domain_element_path, domain_element_value, domain_element_unit): 
        """
        Links/Maps metadata from domain models with SysMLv2 data that the user selected inside the GUI 
        Creates UUIDs for the mapped elements, validates paths, and updates the mapping.json.

        Parameters: 
            sysml_path : String. File path to the directory that contains the sysmlv2 file 
            sysml_element_path : String. Specific path to the element. e.g. package.partA.len
            sysml_element_value : String. Value of the sysml element
            sysml_element_unit : String. Unit of the sysml element value (if provided)
            domain_file_format : String. File Format of specific domain e.g. GerberJobFile or STEP 
            domain_path : String. File path to the directory that contains the domain file 
            domain_element_path : String. Specific path to the element e.g. "GeneralSpecs.Size.X"
            domain_element_value : String. Value of domain element 
        """
        #self.logger.info(f"map_metadata")

        # Validate file existence
        if not os.path.exists(sysml_path):
            self.logger.error(f"SysMLv2 file does not exist: {sysml_path}")
            raise FileNotFoundError(f"SysMLv2 file does not exist: {sysml_path}")
        if not os.path.exists(domain_path):
            self.logger.error(f"Domain file does not exist: {domain_path}")
            raise FileNotFoundError(f"Domain file does not exist: {domain_path}")
        self.logger.info(f"VALIDATION: SysMLv2 filepath: {sysml_path}, VALID: True")
        self.logger.info(f"VALIDATION: Domain filepath: {domain_path}, VALID: True")

        # Load existing mapping.json to extend with data 
        mapping = load_json(file_path=self.mapping_file_path)

        # Generate UUIDs for each element
        uuid_sysml_element = str(uuid.uuid4())
        uuid_domain_element = str(uuid.uuid4())
        #self.logger.debug(f"Generated UUIDs: SysMLv2: {uuid_sysml_element}, Domain: {uuid_domain_element}")

        # Create timestamp
        timestamp = datetime.now().strftime("%d.%m.%Y")

        # Determine datatype 
        def get_datatype(value): 
            # try: 
            #     value = float(value)
            #     return "Real"
            # except ValueError: 
            #     return "String"
            # if isinstance(value, int):
            #     return "Integer"
            # elif isinstance(value, float):
            #     return "Real"
            # elif isinstance(value, str):
            #     try:
            #         float(value)
            #         return "Real"
            #     except ValueError:
            #         return "String"
            # return "Unknown"
            try:
                float(value)
                return "Real"
            except (ValueError, TypeError):
                return "String"        

        sysml_element_datatype = get_datatype(sysml_element_value)
        domain_element_datatype = get_datatype(domain_element_value)
        # Check datatype consistency
        # Both elements have the same datatype and ensure they match
        if sysml_element_datatype and domain_element_datatype:
            if sysml_element_datatype != domain_element_datatype:
                self.logger.error(f"Datatype mismatch: SysMLv2: {sysml_element_datatype}, Domain: {domain_element_datatype}")
                messagebox.showerror("Datatype Mismatch", f"Datatype mismatch: SysMLv2: {sysml_element_datatype}, Domain: {domain_element_datatype}")
                raise ValueError(f"Datatype mismatch: SysMLv2: {sysml_element_datatype}, Domain: {domain_element_datatype}")


        # Check Unit consistency
        # Both elements have the same units and ensure they match
        if sysml_element_unit and domain_element_unit:
            if sysml_element_unit != domain_element_unit:
                self.logger.error(f"Unit mismatch: SysMLv2: {sysml_element_unit}, Domain: {domain_element_unit}")
                messagebox.showerror("Unit Mismatch", f"Unit mismatch: SysMLv2: {sysml_element_unit}, Domain: {domain_element_unit}")
                raise ValueError(f"Unit mismatch: SysMLv2: {sysml_element_unit}, Domain: {domain_element_unit}")
        # Check if only one element has a unit, which is inconsistent
        elif sysml_element_unit or domain_element_unit:
            self.logger.error(f"Unit mismatch: SysMLv2: {sysml_element_unit}, Domain: {domain_element_unit}")
            messagebox.showerror("Unit Mismatch", f"Unit mismatch: SysMLv2: {sysml_element_unit}, Domain: {domain_element_unit}")
            raise ValueError(f"Unit mismatch: SysMLv2: {sysml_element_unit}, Domain: {domain_element_unit}")
        # If neither element has a unit, no validation is needed
        self.logger.info(f"VALIDATION: SysMLv2 unit: {sysml_element_unit}, VALID: True")
        self.logger.info(f"VALIDATION: Domain unit: {domain_element_unit}, VALID: True")

        # Create new element template for mapping.json
        sysml_element = {
            "uuid" : uuid_sysml_element,
            "name" : sysml_element_path.split(".")[-1], #last element from element path 
            "value" : sysml_element_value,
            "unit" : sysml_element_unit, 
            "dataType" : sysml_element_datatype,
            "elementPath" : sysml_element_path,
            "filePath" : sysml_path, 
            "created" : timestamp,
            "lastModified" : timestamp
        }

        domain_element = {
            "uuid" : uuid_domain_element,
            "name" : domain_element_path.split(".")[-1], #last element from element path 
            "value" : domain_element_value,
            "unit" : domain_element_unit, 
            "index" : "0", # Used for precise positioning e.g. #10=CONTEXT_DEPENDENT_SHAPE_REPRESENTATION(#56,#116) -> index : 1 for value #116
            "dataType" : domain_element_datatype,
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

        def log_completeness(element, element_type, required_fields=None):
            # Checks if required fields are existing + if fields have values that are not None, "", []
            if required_fields is None:
                required_fields = element.keys()  
            
            missing_fields = [field for field in required_fields 
                            if field not in element or element[field] in [None, "", []]]
            
            if missing_fields:
                error_msg = f"{element_type} is missing the following fields: {', '.join(missing_fields)}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            else:
                self.logger.info(f"VALIDATION: {element_type} is complete with all required fields.")


        
        #self.logger.debug(f"CHECKING EXISTING MAPPINGS")
        # Check if user selected elements have been already mapped 
        sysml_exists = any(e for e in mapping["SysMLv2"] if e["elementPath"] == sysml_element_path)
        #self.logger.debug(f"sysml element: {sysml_exists}")
        if sysml_exists:
            self.logger.warning(f"SysMLv2 element already exists: {sysml_element_path} at {sysml_path}")
            messagebox.showinfo("Element Exists", f"The SysMLv2 element {sysml_element_path} already exists in the mapping.")
            return False  # Skip adding new mapping


        # Check if Domain element already exists in mapping.json
        domain_exists = any(e for e in mapping.get(domain_file_format, []) if e["elementPath"] == domain_element_path) # and e["filePath"] == domain_path
        #self.logger.debug(f"domain element: {domain_exists}")
        if domain_exists:
            self.logger.warning(f"Domain element already exists: {domain_element_path} at {domain_path}")
            messagebox.showinfo("Element Exists", f"The Domain element {domain_element_path} already exists in the mapping.")
            return False  # Skip adding new mapping

        # Ensure the domain file format exists in the mapping, else create a new section
        if domain_file_format not in mapping:
            #self.logger.debug(f"{domain_file_format} section not found in mapping.json. Creating new section.")
            mapping[domain_file_format] = []

        # Test if domain elementPath is valid aka get_value function works
        if domain_file_format == "GerberJobFile":
           self.logger.debug(f"GERBER")
           self.fp_gerber.file_path = domain_path
           value = self.fp_gerber.get_value(elementPath=domain_element_path) 
           self.logger.debug(f"Value: {value}")
           if not value:
               self.logger.warning(f"Domain Path is not valid!")
               return False

        # Completeness check for sysml_element and domain_element
        # Check if all fields inside sysml_element and domain_element are filled
        required_sysml_fields = ["uuid", "name", "value", "unit", "dataType", "elementPath", "filePath", "created", "lastModified"]
        required_domain_fields = required_sysml_fields + ["index"]

        log_completeness(sysml_element, "SysMLv2", required_fields=required_sysml_fields)
        log_completeness(domain_element, domain_file_format, required_fields=required_domain_fields)

        # Append elements to sysmlv2
        mapping["SysMLv2"].append(sysml_element)
        mapping[f"{domain_file_format}"].append(domain_element)
        mapping["Mappings"].append(new_mapping)

    
        # Save updated mapping.json
        if save_json(file_path=self.mapping_file_path, data=mapping):
            #self.logger.debug(f"Mapping successfully saved at: {self.mapping_file_path}")
            # Update Sysml model (First save mapping.json)
            self.update_sysml_model()
            return True
        else: 
            return False 
        
    def update_sysml_model(self):
        """
        Updates/changes sysml model with domain metadata that has been mapped via mapping.json 
        Overwrites mapped element values (also checks if new values are set from domain files)
        """
        #self.logger.info(f"update_sysml_model")
        # 1) Load mapping.json 
        mapping = load_json(file_path=self.mapping_file_path)

        # 2) Extract relevant domain models (excluding SysMLv2 and Mappings)
        domain_models = {key: value for key, value in mapping.items() if key not in ["SysMLv2", "Mappings"]}
        updated = False
        #self.logger.debug("Checking if there are new values in domain files...")
    
        for domain_name, model in domain_models.items():
            #self.logger.debug(f"Current domain file model: {domain_name}")

            # Ensure model is a list
            if not isinstance(model, list):
                self.logger.warning(f"Skipping {domain_name}, expected a list but found {type(model)}")
                continue
            
            for domain_element in model:  # model is now a list, so iterate directly
                #self.logger.debug(f"Current domain element: {domain_element}")

                # Ensure domain_element is a dictionary
                if not isinstance(domain_element, dict):
                    self.logger.warning(f"Skipping element, expected a dictionary but found {type(domain_element)}")
                    continue

                domain_element_uuid = domain_element.get("uuid")
                domain_element_value = domain_element.get("value")
                domain_elementPath = domain_element.get("elementPath")
                domain_element_filePath = domain_element.get("filePath")

                # Check if file path is valid
                if not domain_element_filePath or not os.path.exists(domain_element_filePath):
                    self.logger.warning(f"File path does not exist: {domain_element_filePath}")
                    continue

                # TODO: select right file parser based on domain file format,  instead of static file parser, select right file parser based on domain file format 
                # Retrieve CURRENT domain element value
                if domain_name == "GerberJobFile": 
                    self.fp_gerber.file_path = domain_element_filePath # Overwrite current file path in file parser object
                    current_domain_element_value = self.fp_gerber.get_value(elementPath=domain_elementPath)
                elif domain_name == "STEP":
                    # Overwrite current file path in file parser object and manually load content again
                    self.fp_step.step_file_path = domain_element_filePath
                    #self.fp_step.load_step_file(step_file_path=domain_element_filePath)
                    current_domain_element_value = self.fp_step.get_value(elementPath=domain_elementPath)

                elif domain_name == "Source Code": 
                    #self.logger.debug(f"Found Source Code. Checking mapped element")
                    #TODO: write get value with elementPath (e.g. @metadata("id", "abc123", "", "string", "PCBDesign", "FlightController.id"))
                    self.fp_code.code_file_path = domain_element_filePath
                    current_domain_element_value = self.fp_code.get_value(elementPath = domain_elementPath)
                else:
                    self.logger.warning(f"Unsupported domain model: {domain_name}. Please add a file parser for this domain model.")
                    continue

                #####################
                if current_domain_element_value:
                    #self.logger.debug(f"Element Path is valid with element value: {current_domain_element_value}")

                    # Update mapping if value has changed
                    if current_domain_element_value != domain_element_value:
                        domain_element["value"] = current_domain_element_value 
                        # Update lastModified with current timestamp
                        timestamp = datetime.now().strftime("%d.%m.%Y")
                        domain_element["lastModified"] = timestamp
                        updated = True
                        #self.logger.debug(f"Updated sysml element in mapping to: {current_domain_element_value}")

                else: 
                    self.logger.warning("Element Path is not valid")

        # Save changes if any updates were made
        if updated:
            save_json(file_path=self.mapping_file_path, data=mapping)
            #self.logger.debug(f"Successfully saved changes from domain file to mapping and sysmlv2 model")

        # 3) Loop through all mappings and update SysMLv2 model with domain metadata
        # Overwrite values of mapped elements in "SysMLv2" with values from "GerberJobFile" etc."
        for mapping_entry in mapping["Mappings"]:
            source_uuid = mapping_entry["sourceUUID"]
            target_uuid = mapping_entry["targetUUID"]

            # Find source and target elements
            source_element = next(
                (elem for domain in domain_models.values() for elem in domain if elem["uuid"] == source_uuid), None) 
            target_element = next(
                (elem for elem in mapping["SysMLv2"] if elem["uuid"] == target_uuid), None)
            
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
            #self.logger.debug(f"Updated content: {updated_content}")
            # Write updated content back to file
            with open(target_file_path, "w") as file:
                file.writelines(updated_content)
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
        #self.logger.info(f"update_value_in_sysml_model")
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
                    #match = re.search(r"^\s*attribute\s+(\w+)\s*(:|=)\s*(\w+|\S+)\s*(;|\s+)", stripped_line)
                    #match = re.search(r"^\s*attribute\s+(\w+)\s*(:|=)\s*(\w+|\S+)(?:\s*(;)?\s*(.*))?$", stripped_line)
                    match = re.search(r"^\s*attribute\s+(\w+)\s*(:|=)\s*([^;]+)(?:\s*(;))?(?:(.*))?$", stripped_line) #[^;] .. everything except optional ; 

                    if match:
                        depth = (len(element_path_splitted)-1)  # we are at the last element of given path 
                        attribute_name = match.group(1)
                        operator = "=" if match.group(2) == ":" else match.group(2)
                        attribute_value = match.group(3)
                        unit_target_value = f"[{unit}]" if is_number and unit else ""
                        # unit_target_value = f"[{unit}]" if is_number else "" 
                        #current_value = match.group(3)
                        semicolon = match.group(4) #or ";"   
                        rest_of_line = match.group(5) 

                        if attribute_name == element_path_splitted[-1]:
                            indentation = " " * (depth * 4)
                            # Replace value of the target element with source value (mapped domain model value)
                            updated_line = f"{indentation}attribute {attribute_name} {operator} {source_value}{unit_target_value}{semicolon}{rest_of_line}\n"
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

