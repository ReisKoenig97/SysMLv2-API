import logging 
import os 
import uuid 
import re # Regex 
from tkinter import messagebox
from tkinter import StringVar

from utils.json_utils import save_json, load_json
from datetime import datetime

class MetadataManager:
    """
    Class to manage metadata between domain models and SysMLv2
    Writes, extracts and maps data inside a mapping.json
    Creates UUIDS for each mapped element inside mapping.json 
    Responsible for versioning, commits and traceability 
    """
    def __init__(self, config, versioncontrol=None, gerberparser=None, stepparser=None, codeparser=None, AUTOSARparser=None, sysmlparser=None, default_sysml_element_write_prio=1):
        self.logger = logging.getLogger(__name__ + "-MetadataManager")
        #self.logger.info(f"Initialized MetadataManager")
        
        self.config = config
        self.mapping_template_file_path = "./config/mapping_template.json"
        self.mapping_file_path = "./config/mapping.json"
        self.change_log_path = "./change_log.json"
        # NOTE: not only dependend on repo path inside config.json also dependend on which OS the mapping has been made
        self.repo_path = self.config["repo_path"] # Change it between windows and macOS 
        self.vc = versioncontrol
        self.fp_gerber = gerberparser
        self.fp_step = stepparser 
        self.fp_code = codeparser
        self.fp_AUTOSAR = AUTOSARparser
        self.fp_sysml = sysmlparser

        self.default_sysml_element_write_prio = default_sysml_element_write_prio

        
        # Parameters will be set later by functions 
        self.sysml_model = None
        self.domain_model = None
        self.app = None #reference to GUI instance
        # List of keywords for regex search inside the sysml file 
        self.keywords = ["part", "part def", "package", "attribute",""]
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
        
    def map_metadata(self, sysml_path, sysml_element_path, sysml_element_value, sysml_element_unit, domain_file_format, domain_path, domain_element_path, domain_element_value, domain_element_unit, domain_element_write_prio): 
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
        if domain_file_format == "AUTOSAR":
            AUTOSAR_elem = self.fp_AUTOSAR.find_elem(domain_element_path)
            AUTOSAR_elem_parent = self.fp_AUTOSAR.parent_map.get(AUTOSAR_elem)
            if AUTOSAR_elem_parent != None and AUTOSAR_elem_parent.get("UUID") != None and domain_element_path.split(".")[-1]=="SHORT-NAME":
                uuid_domain_element = self.fp_AUTOSAR.parent_map.get(AUTOSAR_elem).get("UUID")
                self.logger.info(f"[MetadataManager:map_metadata()]: Element at {domain_element_path} got UUID {uuid_domain_element} from arxml file")
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


        #validate write_prio
        if not domain_element_write_prio.isdigit():
            self.logger.error(f"invalid write_prio: {domain_element_write_prio}")
            messagebox.showerror("invalid Write Prio","please enter a valid write_prio, i.e. a positive integer number")
            return False
        
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
            "write_prio":str(self.default_sysml_element_write_prio),
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
            "write_prio":domain_element_write_prio,
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
                            if field not in element or element[field] in [None]] #removed "" and []
            
            if missing_fields:
                error_msg = f"{element_type} is missing the following fields: {', '.join(missing_fields)}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
            else:
                self.logger.info(f"VALIDATION: {element_type} is complete with all required fields.")


        
        #self.logger.debug(f"CHECKING EXISTING MAPPINGS")
        # Check if user selected elements have been already mapped
        sysml_elements_with_same_path = [e for e in mapping["SysMLv2"] if e["elementPath"] == sysml_element_path and e["filePath"]==sysml_path]
        sysml_exists = False
        if len(sysml_elements_with_same_path) == 1: sysml_exists = True
        if len(sysml_elements_with_same_path) > 1:
            self.logger.error(f"there are more than one sysml elements with path {sysml_path} / {sysml_element_path} in {self.mapping_file_path}")
            return False
        self.logger.debug(f"sysml element: {sysml_exists}")
        if sysml_exists:
            new_mapping["targetUUID"] = sysml_elements_with_same_path[0]["uuid"]
            mapped_domain_elements = self.get_mapped_domain_elements(sysml_elements_with_same_path[0]["uuid"])
            if domain_element_write_prio != "0" and domain_element_write_prio in [element["write_prio"] for element in mapped_domain_elements] or sysml_elements_with_same_path[0]["write_prio"]==domain_element_write_prio:#Many to one mapping with element that has same Write Prio
                error_msg_double_write_prio = f"there is already an element with Write Prio {domain_element_write_prio}. Please select another!\nOccupied Values are: {sysml_elements_with_same_path[0]["write_prio"]}"
                for domain_element in mapped_domain_elements:
                    if domain_element["write_prio"] != "0":
                        error_msg_double_write_prio = f"{error_msg_double_write_prio}, {domain_element["write_prio"]}"
                self.logger.error(f"there is already an element with Write Prio {domain_element_write_prio}")
                messagebox.showerror("wrong Write Prio", error_msg_double_write_prio)
                return False



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
           if value == None:
               self.logger.warning(f"Domain Path is not valid!")
               return False
           #Check if AUTOSAR-ElementPath is valid
        if domain_file_format == "AUTOSAR":
            element = self.fp_AUTOSAR.find_elem(domain_element_path)
            
            if element == None: 
                self.logger.warning("AUTOSAR Domain Path is not valid!")
                return False
            AUTOSAR_only_path = self.fp_AUTOSAR.get_AUTOSAR_only_path(element)[1:].replace("/",".")
            domain_element["parent_uuid"]=self.fp_AUTOSAR.find_elem(AUTOSAR_only_path).get("UUID")
            domain_element["index"]=len(AUTOSAR_only_path.split("."))#first occurence of Tag element

        # Completeness check for sysml_element and domain_element
        # Check if all fields inside sysml_element and domain_element are filled
        required_sysml_fields = ["uuid", "name", "value", "dataType","write_prio", "elementPath", "filePath", "created", "lastModified"]#removed "unit"
        required_domain_fields = required_sysml_fields + ["index"]

        log_completeness(sysml_element, "SysMLv2", required_fields=required_sysml_fields)
        log_completeness(domain_element, domain_file_format, required_fields=required_domain_fields)

        # Append elements to sysmlv2
        if not sysml_exists: 
            mapping["SysMLv2"].append(sysml_element)
            self.update_change_log(sysml_element["uuid"],sysml_element["value"],"Generated by mapping Tool")
        mapping[f"{domain_file_format}"].append(domain_element)
        self.update_change_log(domain_element["uuid"],domain_element["value"],"Generated by mapping Tool")
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
        self.logger.info(f"[MetadataManager:update_sysml_model()]: attemting to update sysml Model at {self.fp_sysml.sysml_path} with mapping at {self.mapping_file_path}")
        #self.logger.info(f"update_sysml_model")
        # 1) Load mapping.json 
        mapping = load_json(file_path=self.mapping_file_path)

        # 2) Extract relevant domain models (excluding SysMLv2 and Mappings)
        domain_models = {key: value for key, value in mapping.items() if key not in ["SysMLv2", "Mappings"]}
        all_models = {key: value for key, value in mapping.items() if key != "Mappings"}

        updated = False
        #self.logger.debug("Checking if there are new values in domain files...")
    
        for domain_name, model in all_models.items():
            #self.logger.debug(f"Current domain file model: {domain_name}")

            # Ensure model is a list
            if not isinstance(model, list):
                self.logger.warning(f"[MetadataManager:update_sysml_model()]: Skipping {domain_name}, expected a list but found {type(model)}")
                continue
            
            for domain_element in model:  # model is now a list, so iterate directly
                #self.logger.debug(f"Current domain element: {domain_element}")

                # Ensure domain_element is a dictionary
                if not isinstance(domain_element, dict):
                    self.logger.warning(f"[MetadataManager:update_sysml_model()]: Skipping element, expected a dictionary but found {type(domain_element)}")
                    continue

                domain_element_uuid = domain_element.get("uuid")
                domain_element_value = domain_element.get("value")
                domain_elementPath = domain_element.get("elementPath")
                domain_element_filePath = domain_element.get("filePath")

                # Check if file path is valid
                if not domain_element_filePath or not os.path.exists(domain_element_filePath):
                    self.logger.warning(f"[MetadataManager:update_sysml_model()]: File path does not exist: {domain_element_filePath}")
                    continue

                # TODO: select right file parser based on domain file format,  instead of static file parser, select right file parser based on domain file format 
                # Retrieve CURRENT domain element value
                if domain_name == "GerberJobFile": 
                    self.fp_gerber.file_path = domain_element_filePath # Overwrite current file path in file parser object
                    current_domain_element_value = self.fp_gerber.get_value(elementPath=domain_elementPath)
                elif domain_name == "STEP":
                    # Overwrite current file path in file parser object and manually load content again
                    self.fp_step.step_file_path = domain_element_filePath

                    current_domain_element_value = self.fp_step.get_value(elementPath=domain_elementPath)

                elif domain_name == "Source Code": 
                    #self.logger.debug(f"Found Source Code. Checking mapped element")
                    self.fp_code.code_file_path = domain_element_filePath
                    current_domain_element_value = self.fp_code.get_value(elementPath = domain_elementPath)
                elif domain_name == "AUTOSAR":
                    self.fp_AUTOSAR.file_path = domain_element_filePath
                    current_domain_element_value = self.fp_AUTOSAR.get_value(elementPath = domain_elementPath, reload_file = True, uuid=domain_element["parent_uuid"],mapping=mapping)
                elif domain_name == "SysMLv2":
                    self.fp_sysml.sysml_path = domain_element_filePath
                    current_domain_element_value = self.fp_sysml.get_value(elementPath = domain_elementPath)
                else:
                    self.logger.warning(f"[MetadataManager:update_sysml_model()]: Unsupported domain model: {domain_name}. Please add a file parser for this domain model.")
                    continue

                #####################
                if current_domain_element_value != None:
                    #self.logger.debug(f"Element Path is valid with element value: {current_domain_element_value}")

                    # Update mapping if value has changed
                    if current_domain_element_value != domain_element_value:
                        domain_element["value"] = current_domain_element_value
                        # Update lastModified with current timestamp
                        timestamp = datetime.now().strftime("%d.%m.%Y")
                        domain_element["lastModified"] = timestamp
                        self.update_change_log(domain_element["uuid"],current_domain_element_value,"Updated by value change in Domain file")
                        #self.logger.debug(f"Updated sysml element in mapping to: {current_domain_element_value}")

                else: 
                    self.logger.warning("Element Path is not valid")

        # Save changes if any updates were made
        self.logger.info(f"[MetadataManager:update_sysml_model()]: mapping file was successfully updated. proceeding")
        
        save_json(file_path=self.mapping_file_path, data=mapping)
            
        self.logger.info(f"[MetadataManager:update_sysml_model()]: mapping file was successfully updated. proceeding to consistency management")
        #check for inconsistent values between sysml and their mapped elements
        self.manage_consistency()
        return
        
        
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
        content = content.split("\n")
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
                    match = re.search(r"^\s*(?:attribute\s+)?([\w-]+)\s*(:|=)\s*([^;#]+?)\s*(;)?\s*(#.*)?$", stripped_line) #[^;] .. everything except optional ; 

                    if match:
                        depth = (len(element_path_splitted)-1)  # we are at the last element of given path 
                        attribute_name = match.group(1)
                        operator = "=" if match.group(2) == ":" else match.group(2)
                        attribute_value = match.group(3)
                        unit_target_value = f"[{unit}]" if is_number and unit else ""
                        semicolon = match.group(4) #or ";"   
                        rest_of_line = match.group(5) 
                        if rest_of_line == None: rest_of_line=""

                        if attribute_name == element_path_splitted[-1]:
                            indentation = " " * (depth * 4)
                            attribute_str = ""
                            if stripped_line.startswith("attribute"): attribute_str = "attribute "
                            # Replace value of the target element with source value (mapped domain model value)
                            updated_line = f"{indentation}{attribute_str}{attribute_name} {operator} {source_value}{unit_target_value}{semicolon}{rest_of_line}"
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


    def manage_consistency(self):
        """
        Create a conflict_list tuples of (sysml_element,domain_elements, most_current_value) and call GUI functions to manage inconsistencies, if there anre any.
        If there are no conflicts, return without any changes
            sysml_element: a sysml_element from mapping.json
            domain_elements: list of all domain elements that are mapped to sysml_element
            most_current_value: value to which the value of all elements should be changed to according to write_prio i.e. the value of the Element with the highest write_prio value
        Such a tuple is added to conflict_list, if any value in the domain element list or the sysml element value is different from another
        conflict_list is then passed to GUI.popup_conflict_manager() where a ttk.Toplevel Widget is created where the User decides which changes are to be discarded and which are to be taken
        from that choice, a list of tuples selection_list ((model_element_uuid,new_value),selection_var) is created
            model_element_uuid: uuid of a model_element that has a value to be changed to new_value, if selection_var == 1
            new value: value to which the elements value shall be changed to
            selection_var: StringVar. If 1: values must be changed, if 0: value must not be changed
        each tuple references an element in mapping.json, whose value has been decided to be updated to new_value or not.  new_value is the most_current_value for that element
        this list will be passed to apply_value_changes_to_mapping() where the changes are propagated and saved to mapping.json and the domain files
        :return: Nothing, desired effects are achieved in apply_value_changes_to_mapping(). Function Call order: manage_consistency -> popup_consistency_manager -> apply_value_changes_to_mapping
        """
        self.logger.info("[MetadataManager:manage_consistency()]: starting consistency management")
        if not os.path.exists(self.mapping_file_path):
            self.logger.error(f"[MetadataManager:manage_consistency()]: path does not exist: {self.mapping_file_path}")
            raise FileNotFoundError(f"[MetadataManager:manage_consistency()]: Mapping file does not exist: {self.mapping_file_path}")

        # load mapping data
        mapping = load_json(file_path=self.mapping_file_path)
        domain_models = {key: value for key, value in mapping.items() if key not in ["SysMLv2", "Mappings"]}
        sysml_model = mapping["SysMLv2"]
        mappings = mapping["Mappings"]
        
        if not isinstance(sysml_model, list) or not isinstance(mappings, list):
            self.logger.error(f"[MetadataManager:manage_consistency()]: Error: sysml_model or mappings are not in list Format")
            return None
        conflict_list = []  #list of conflicting(different values for same mapped parameter) sysml_model_elements and their mapped domain elements; Format: [sysml_model_element,[mapped_domain_model_elements],most_current_value_according_to_write_prio]
        self.logger.info(f"[MetadataManager:manage_consistency()]: successfully loaded mapping file")

        #iterate through sysml model elements and add conflicting elements to conflict_list
        for sysml_model_element in sysml_model:
            if not isinstance(sysml_model_element, dict):
                self.logger.warning(f"[MetadataManager:manage_consistency()]: Warning: sysml_model_element: {sysml_model_element} is not a dict -> skipping element")
                continue
            mapped_domain_elements = self.get_mapped_domain_elements(sysml_model_element["uuid"], domain_models, mappings)

            if self.value_conflict_exists(sysml_model_element, mapped_domain_elements):
                max_write_prio_element = self.get_max_write_prio_element(mapped_domain_elements)

                if int(max_write_prio_element["write_prio"]) < int(sysml_model_element["write_prio"]):
                    max_write_prio_element = sysml_model_element

                most_current_value = max_write_prio_element["value"]
                conflict_list.append((sysml_model_element, mapped_domain_elements, most_current_value))

        #open Toplevel window to let the User decide what value_changes to discard
        self.logger.info(f"[MetadataManager:manage_consistency()]: successfully generated Conflict list of length {len(conflict_list)}")
        if len(conflict_list) > 0: self.app.popup_conflict_manager(conflict_list)#generates change_list of Format [(element_uuid,new_value)]
        return

    def apply_value_changes_to_mapping(self, selection_list):
        """
        :param selection_list: list of tuples ((model_element_uuid, new_value),selection_var)
            model_element_uuid: uuid of a model_element that has a value to be changed to new_value, if selection_var == 1
            new value: value to which the elements value shall be changed to
            selection_var: Stringvar. If 1: values must be changed, if 0: value must not be changed
        :return: True if changes were propagated and saved successfully to mapping and domain files; else False
        """
        self.logger.info(f"[MetadataManager:apply_value_changes_to_mapping()]: attemting to apply changes defined by selection List")
        if not isinstance(selection_list,list):
            self.logger.error("[MetadataManager:apply_value_changes_to_mapping()]: selection_list is not of type list")
            return False
        
        #check if selection item format is ((str,str),StringVar)

        if len(selection_list) > 0 and not all(isinstance(selection_item, tuple) and len(selection_item) == 2 and 
                   #isinstance(selection_item[1], StringVar) and
                   isinstance(selection_item[0], tuple) and len(selection_item[0]) == 2 and
                   isinstance(selection_item[0][0], str) and isinstance(selection_item[0][1], str)
                   for selection_item in selection_list):
            self.logger.error("[MetadataManager:apply_value_changes_to_mapping()]: selection item is not of Type ((str,str),strvar)")
            return False
        
        #check if path to mapping exists
        if not os.path.exists(self.mapping_file_path):
            self.logger.error(f"[MetadataManager:apply_value_changes_to_mapping()]: Mapping file path does not exist: {self.mapping_file_path}")
            return False
        
        self.logger.info(f"[MetadataManager:apply_value_changes_to_mapping()]: input parameters are valid. proceeding to load mapping file")
        #load mapping file
        mapping = load_json(file_path=self.mapping_file_path)
        self.logger.info(f"[MetadataManager:apply_value_changes_to_mapping()]: mapping file loaded successfully. proceeding to change values in mapping and domain files")

        """
        create change_list of format [(model_element_uuid,new_value)]
        each tuple is in change_list, if selection_var for that tuple is 1 in selection_list
        """
        change_list = [update_tuple for update_tuple, selection_var in selection_list if (isinstance(selection_var,int) and selection_var == 1) or (not isinstance(selection_var,int) and selection_var.get() == "1")]  #returns list of Format [(model_element_uuid, new_value)]

        #iterate through change list, find affected elements in mapping.json and change their values
        for uuid, new_value in change_list:
            self.logger.info(f"[MetadataManager:apply_value_changes_to_mapping()]: attemt to update model_element with uuid = {uuid} to new value = {new_value}")
            model_element_to_change = self.get_model_element(uuid, {model_name: model for model_name, model in mapping.items() if model_name != "Mappings"})
            if model_element_to_change == None:
                self.logger.error(f"[MetadataManager:apply_value_changes_to_mapping()]: could not find Element with uuid = {uuid} that has to be changed in mapping.json ")
                return False
            if model_element_to_change["value"] != new_value:
                self.logger.info(f"[MetadataManager:apply_value_changes_to_mapping()]:     updating value in mapping file because it was different before")
                model_element_to_change["value"] = new_value
                model_element_to_change["lastModified"]= datetime.now().strftime("%d.%m.%Y")
                self.update_change_log(model_element_to_change["uuid"],new_value,"Updated by consistency Management")
                #propagate changes to domain files
                self.logger.info(f"[MetadataManager:apply_value_changes_to_mapping()]:     updating value to domain file")
                for domain_name, domain_model in mapping.items():
                    
                    if domain_name == "Mappings": continue
                    if model_element_to_change["uuid"] in [element["uuid"] for element in domain_model]:
                        self.logger.info(f"[MetadataManager:apply_value_changes_to_mapping()]:      model with uuid {model_element_to_change["uuid"]} has to be changed in its domain file and is part of domain {domain_name}")
                        if domain_name == "SysMLv2": 
                            self.fp_sysml.sysml_path = model_element_to_change["filePath"]
                            updated_content = self.update_value_in_sysml_model(self.fp_sysml.load_sysml_model(),model_element_to_change["elementPath"],model_element_to_change["value"],model_element_to_change["unit"])
                            updated_content_str = ""
                            for line in updated_content[:-1]: updated_content_str = f"{updated_content_str}{line}\n"
                            updated_content_str += updated_content[-1]
                            try:
                                with open(f"{self.fp_sysml.sysml_path}", "w") as sysml_file:
                                    sysml_file.write(updated_content_str)
                            except Exception:
                                self.logger.error(f"[MetadataManager:apply_value_changes_to_mapping()]:     error writing to {self.fp_sysml.sysml_path}")
                        elif domain_name == "AUTOSAR": 
                            self.fp_AUTOSAR.load_file(model_element_to_change["filePath"])
                            self.fp_AUTOSAR.set_value(model_element_to_change["elementPath"],model_element_to_change["value"],mapping)
                        elif domain_name in ["GerberJobFile","STEP","Source Code"]:
                            self.logger.warning(f"[MetadataManager:apply_value_changes_to_mapping()]: {domain_name} has not yet implemented a set_value_function")
                        else:
                            self.logger.error(f"[MetadataManager:apply_value_changes_to_mapping()]: unknown Domain Name: {domain_name}")

        #save changes
        save_json(file_path=self.mapping_file_path, data=mapping)
        self.logger.info(f"[MetadataManager:apply_value_changes_to_mapping()]: value changes have been saved successfully")
        return True
    
    def get_Mappings_elements(self, mapping=None):
        """
        get data about all "Mappings" entries in mapping. json
        :param mapping: complete content of mapping file. If None, it will be generated from the mapping file at self.mapping_file_path
        :return: list of Tuples (mapping_element, sysml_element, domain_model_element) for each "Mappings" entry in mapping.json
            mapping_element: "Mappings" element from mapping.json
            sysml_element: sysml element to which the mapping_element refers to
            domain_model_element: Domain model element to which the mapping_element refers to
        """
        #load mapping file
        self.logger.info(f"[MetadataManager:get_Mappings_elements()]: attemting to get mappings elements")
        if mapping == None: mapping = load_json(self.mapping_file_path)
        domain_models = {model_name: model_elements for model_name, model_elements in mapping.items() if model_name not in  ["Mappings","SysMLv2"]}
        sysml_model = mapping["SysMLv2"]
        mappings = mapping["Mappings"]
        self.logger.info(f"[MetadataManager:get_Mappings_elements()]: mapping loaded successfully. Proceeding to generate list of mappings")
        mappings_elements = [] #Format (mapping_element, sysml_model_element, domain_model_element)

        #create tuples and append them to mappings list
        for  mappings_element in mappings:
            sysml_element = self.get_model_element(mappings_element["targetUUID"],sysml_model)
            domain_element = self.get_model_element(mappings_element["sourceUUID"],domain_models)
            mappings_elements.append((mappings_element,sysml_element,domain_element))

        #return mappings_elements
        if mappings_elements == []:
            self.logger.warning("[MetadataManager:get_Mappings_elements()]: mappings_elements list is empty: no 'Mappings' entries available in mapping.json")
        
        self.logger.info(f"[MetadataManager:get_Mappings_elements()]: Mappings elements list generated successfully")
        return mappings_elements
    
    def remove_mapping(self, target_uuid, source_uuid):
        """
        remove Mappings entry with target_uuid=target_uuid and source_uuid=source_uuid and their domain model element and sysml element that are mapped to it
        if sysml element has other domain elements mapped to it, it will not be removed
        :param target_uuid: target uuid of "Mappings" element; also uuid of sysml element to be removed
        :param source_uuid: source uuid of "Mappings" element; also uuid of domain model element to be removed
        :return: True if deletion was successful; else False
        """
        self.logger.info(f"[MetadataManager:remove_mapping()]: attemting to remove mapping with target_uuid = {target_uuid} and source_uuid = {source_uuid}")
        mapping = load_json(self.mapping_file_path)
        domain_models = {model_name: model_elements for model_name, model_elements in mapping.items() if model_name != "Mappings"}
        sysml_model = mapping["SysMLv2"]
        mappings = mapping["Mappings"]

        mapped_domain_elements = self.get_mapped_domain_elements(target_uuid,domain_models,mappings)
        if not mapped_domain_elements or mapped_domain_elements == []:
            self.logger.error("[MetadataManager:remove_mapping()]: there are no elements mapped to sysml_element with uuid=target_uuid")
            return False
        #validate that mapping is valid and exists
        if len([domain_model_element for domain_model_element in mapped_domain_elements if domain_model_element["uuid"] == source_uuid]) != 1:#list that contains all domain model elements with uuid=source_uuid mapped to sysml model element with uuid=target_uuid. len should be 1
            self.logger.error("[MetadataManager:remove_mapping()]: target_uuid or source_uuid are either not in mapping.json or not mapped together")
            return False
        
        self.logger.info(f"[MetadataManager:remove_mapping()]: input parameters are valid. Proceeding to remove mapping")
        #delete mappings_element

        mapping["Mappings"] = [mappings_element for mappings_element in mapping["Mappings"] if mappings_element["targetUUID"] != target_uuid or mappings_element["sourceUUID"] != source_uuid]

        #delete sysml element with uuid=target_uuid if no other domain model element is mapped to it
       
        if len(mapped_domain_elements) > 1:
            self.logger.warning("[MetadataManager:remove_mapping()]: There are other elements mapped to the sysml_element -> skipping deletion of sysml_element")
        else:
            mapping["SysMLv2"] = [sysml_element for sysml_element in mapping["SysMLv2"] if sysml_element["uuid"] != target_uuid]
            #remove sysml Element from chenge_history
            self.delete_change_log_element(target_uuid)
       
        #delete mapped domain model element(s)
        for domain_name, domain_model in domain_models.items():
            mapping[domain_name] = [domain_model_element for domain_model_element in mapping[domain_name] if domain_model_element["uuid"] != source_uuid]
            #remove sysml Element from chenge_history
        self.delete_change_log_element(source_uuid)

        #save changes
        save_json(file_path=self.mapping_file_path, data=mapping)
        self.logger.info(f"[MetadataManager:remove_mapping()]: mapping removed successfully")
        return True

    """
    Helper Functions for consistency management
    """

    def get_mapped_domain_elements(self, sysml_model_element_uuid, models=None, mapping=None):
        """
        get all domain model elements in models that are mapped to the sysml model element with uuid=sysml_model_element_uuid according to mapping
        :param sysml_model_element_uuid: uuid of the sysml_model to which the mapped domain model elements are searched for
        :param models: dictionary of Domain models, each model contains a list of domain model elements. If None, it will be generated from self.mapping_file_path
        :param mapping: list of "Mappings" elements from mapping.json. If None, it will be generated from self.mapping_file_path
        :return: list of domain elements that are mapped to the sysml model element with sysml_model_element_uuid
            [] if there are none
            None on error
        """
        self.logger.info(f"[MetadataManager:get_mapped_domain_elements()]: attemting to get domain model elements mapped to sysml model element with uuid {sysml_model_element_uuid}")
        if models == None:
            mapping_content = load_json(self.mapping_file_path)
            models = {model_name: model_elements for model_name, model_elements in mapping_content.items() if model_name != "Mappings"}

            
        if mapping == None:
            mapping_content = load_json(self.mapping_file_path)
            mapping = mapping_content["Mappings"]
            

        if not isinstance(models, dict):
            self.logger.error("[MetadataManager:get_mapped_domain_elements()]: models provided are not of type dict")
            return None
        if not isinstance(mapping,list):
            self.logger.error(f"[MetadataManager:get_mapped_domain_elements()]: mapping is not of type list: type is {type(mapping)}")
            return None        
        if not sysml_model_element_uuid or sysml_model_element_uuid == "":
            self.logger.error("[MetadataManager:get_mapped_domain_elements()]: sysml_model_elemet_uuid is None or empty String")
            return None

        self.logger.info(f"[MetadataManager:get_mapped_domain_elements()]: input parameters are valid. Proceeding to get mapped elements")
        mapped_domain_elements = []
        domain_model_element_uuids = []
        #iterate through Elements in mapping an get uuids of the domain model elements
        for mapping_element in mapping:
            if mapping_element["targetUUID"] == sysml_model_element_uuid:
                domain_model_element_uuids.append(mapping_element["sourceUUID"])
        #iterate through model elements and add all elements with fitting uuid to mapped_domain_elements
        for model in models.values():
            for model_element in model:
                if model_element["uuid"] in domain_model_element_uuids:
                    self.logger.info(f"[MetadataManager:get_mapped_domain_elements()]:      found element with uuid = {model_element["uuid"]}")
                    mapped_domain_elements.append(model_element)

        self.logger.info(f"[MetadataManager:get_mapped_domain_elements()]: successfully generated mapped domain element list")
        return mapped_domain_elements

    def get_model_element(self, model_element_uuid, models=None):
        """
        get Model element from models by uuid
        :param model_element_uuid: uuid of model_element that is searched in models
        :param models: dictionary or list of models. each dict Entry contains a list of model elements. If None, it will be generated from self.mapping_file_path
        :return: model element with uuid model_element_uuid
        None if not found
        """
        # load all models from mapping.json as dict if no model list or dict is provided
        self.logger.info(f"[MetadataManager:get_model_element()]: attemting to get model element with uuid = {model_element_uuid}")
        if models == None:

            mapping = load_json(self.mapping_file_path)
            models = {model_name: model_elements for model_name, model_elements in mapping.items() if model_name != "Mappings"}

        # if models is a dict, turn it to a flatened list of model_elements
        if isinstance(models, dict): 

            flattened_model_list = []
            for model in models.values():
                flattened_model_list.extend(model)
            models = flattened_model_list

        if not isinstance(models,list):
            self.logger.error("[MetadataManager:get_model_element()]: models is not of type list at this point in the function")
            return None
        self.logger.info(f"[MetadataManager:get_model_element()]: input parameters are valid. proceeding to search for element")
        #find element
        for model_element in models:

            if model_element["uuid"] == model_element_uuid:
                self.logger.info(f"[MetadataManager:get_model_element()]: found model Element with uuid = {model_element["uuid"]}")
                return model_element

        #return element
        self.logger.warning(f"[MetadataManager:get_model_element()]: No model Element found with uuid: {model_element_uuid}")
        return None

    def get_max_write_prio_element(self, model_elements):
        """
        get the element with the highest "write_prio" value in model_elements.
        In case of tie, first element with highest "write_prio" value in model elements
        :param model_elements: list of model_elements from mapping.json
        :return: first model element with the highest "write_prio" value
            None if error
        """
        self.logger.info(f"[MetadataManager:get_max_write_prio_element()]: attemting to get max write prio element")

        if not model_elements or not isinstance(model_elements, list):
            self.logger.error("[MetadataManager:get_max_write_prio_element()]: model_elements is None, or of wrong type")
            return None
        
        self.logger.info(f"[MetadataManager:get_max_write_prio_element()]: input parameters are valid. Proceeding to search for max write prio element")
        max_element = None
        for model_element in model_elements:
            if not isinstance(model_element, dict):
                self.logger.warning(f"[MetadataManager:get_max_write_prio_element()]: element {model_element} is not of type dict -> skipping Element")
                continue
            if max_element == None or int(max_element["write_prio"]) < int(model_element["write_prio"]):
                max_element = model_element

        if max_element == None:
            self.logger.warning("[MetadataManager:get_max_write_prio_element()]: Max_write_prio_element is none; returning None")
            return None
        self.logger.info(f"[MetadataManager:get_max_write_prio_element()]: successfully found max write prio element of write_prio = {max_element["write_prio"]}")
        return max_element

    def value_conflict_exists(self, sysml_element, mapped_domain_elements):
        """
        Return if ["value"] attribute for any element in mapped_domain_elements and sysml_element differs from another (value conflict)
        :param sysml_element: sysml element from mapping.json
        :param mapped_domain_elements: list of domain elements from mapping.json
        :return: Boolean: True if Value Conflict; False if no Value Conflict
            None on error
        """
        self.logger.info(f"[MetadataManager:value_conflict_exists()]: attemting to check if value conflict exists")
        if sysml_element == None:
            self.logger.error("[MetadataManager:value_conflict_exists()]: sysml_element is None")
            return None
        if mapped_domain_elements == None:
            self.logger.error("[MetadataManager:value_conflict_exists()]: mapped_domain_elements is None")
            return None
        if not isinstance(sysml_element,dict):
            self.logger.error("[MetadataManager:value_conflict_exists()]: sysml_element is not of type dict")
            return None
        if not isinstance(mapped_domain_elements,list):
            self.logger.error("[MetadataManager:value_conflict_exists()]: mapped_domain_elements is not of type list")
            return None
        self.logger.info(f"[MetadataManager:value_conflict_exists()]: input parameters are valid. Proceeding to check for value conflicts")
        for mapped_domain_element in mapped_domain_elements:
            if not isinstance(mapped_domain_element, dict):
                self.logger.warning(f"[MetadataManager:value_conflict_exists()]: element {mapped_domain_element} is not of type dict -> skipping Element")
                continue
            if mapped_domain_element["value"] != sysml_element["value"]:
                self.logger.info(f"[MetadataManager:value_conflict_exists()]: value Conflict found at mapped domain element with uuid = {mapped_domain_element["uuid"]}")
                return True
        self.logger.info(f"[MetadataManager:value_conflict_exists()]: No Value Conflict found")
        return False
    
    def update_change_log(self,uuid, value, changed_by):
        """
        add element to change history of Element with UUID = uuid
        :param uuid: UUID of the element that shall be updated
        :param value: new Value of the Element
        :param changed_by: String that describes why the element's value has been changed to value
        :return: True if deletion was successful; else False
        """
        self.logger.info(f"[MetadataManager:update_change_log()]: updating changelog element with uuid = {uuid} to {value} with reason: {changed_by}")
        if uuid == None or uuid == "":
            self.logger.error(f"[MetadataManager:update_change_log()]: invalid uuid: {uuid}")
            return False
        if value == None:
            self.logger.error(f"[MetadataManager:update_change_log()]: value is None")
            return False
        if not isinstance(changed_by,str) or changed_by == None:
            self.logger.error(f"[MetadataManager:update_change_log()]: invalid change reason: {changed_by}")
            return False
        self.logger.info(f"[MetadataManager:update_change_log()]: input parameters are valid. proceeding...")
        #load changelog file
        change_log = load_json(self.change_log_path)
        #check if uuid exists:
        if change_log.get(uuid) == None:
            change_log[uuid] = []
        
        change_log_item = {
            "n_change": len(change_log[uuid]),
            "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "value": value,
            "changed_by": changed_by
        }
        change_log[uuid].append(change_log_item)
        save_json(data=change_log,file_path=self.change_log_path)
        self.logger.info(f"[MetadataManager:update_change_log()]: successfully updated change log element")
        return True
    
    def delete_change_log_element(self, uuid):
        """
        delete change history of Element with UUID = uuid
        :param uuid: UUID of the element that shall be removed
        :return: True if deletion was successful; else False
        """
        self.logger.info(f"[MetadataManager:delete_change_log_element()]: removing Element with uuid = {uuid}")
        if uuid == None or uuid == "":
            self.logger.error(f"[MetadataManager:delete_change_log_element()]: invalid uuid: {uuid}")
            return False
        self.logger.info(f"[MetadataManager:delete_change_log_element()]: input parameter valid. proceeding...")
        change_log = load_json(self.change_log_path)
        if change_log.get(uuid) == None:
            self.logger.error(f"[MetadataManager:delete_change_log_element()]: uuid is not in changelog: {uuid}")
            return False
        change_log.pop(uuid)
        save_json(data=change_log,file_path=self.change_log_path)
        self.logger.info(f"[MetadataManager:delete_change_log_element()]: deletion was succesful")
        return True
    
    def get_change_log(self):
        """
        :return: changelog as dict
        """
        self.logger.info(f"[MetadataManager:get_change_log()]: returning change_log")
        return load_json(self.change_log_path)
