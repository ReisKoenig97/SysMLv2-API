import xml.etree.ElementTree as ET
import logging
import os
from utils.json_utils import save_json, load_json
from datetime import datetime

class AUTOSAR_Parser:
    """
    Parser class to 
        load Data from arxml file
        save Data to an arxml file
    """
    def __init__(self,AUTOSAR_file_path=None):
        self.file_content_str = None  # arxml-File Content as String
        self.file_content_tree = None  # arxml-File Content as elementTree
        self.tree_root = None         # root of file_content_tree
        self.parent_map = None      #dictionary of child:parent pairs
        self.file_path = AUTOSAR_file_path         #Path to arxml-File
        self.mapping_file_path = None
        self.logger = logging.getLogger(__name__+"AUTOSAR_Parser")
        if self.file_path: self.load_file(self.file_path)

    def load_file(self, file_path=None):

        """
        :param file_path: path to arxml-file; if not set, take self.file_path
        :return: self.file_content_tree, if file was loaded amd self.tree_root, self.file_content_str and self.file_content_tree were set
                Else None
        """
        self.logger.info(f"[AUTOSAR_Parser:load_file()]: attemting to load AUTOSAR-File at {file_path}")
        if file_path != None: self.file_path = file_path

        # check if file_path is set and exists
        if not self.file_path or self.file_path == "":
            self.logger.warning(f"[AUTOSAR_Parser:load_file()]: AUTOSAR arxml file is not provided.")
            return None
        if not os.path.exists(self.file_path):
            self.logger.error(f"[AUTOSAR_Parser:load_file()]: Error: File {self.file_path} does not exist")
            return None
        self.logger.info(f"[AUTOSAR_Parser:load_file()]: file path is valid. Loading contents into Parser...")
        # open File
        try:
            with open(self.file_path, "r") as file:
                self.file_content_str = file.readlines()
                self.file_content_tree = ET.parse(self.file_path)
                self.tree_root = self.file_content_tree.getroot()
                #soruce: https://sqlpey.com/python/how-to-access-parent-nodes-in-python-elementtree/#practical-example
                self.parent_map = {child: parent for parent in self.file_content_tree.iter() for child in parent}

        except Exception as e:
            self.logger.error(f"[AUTOSAR_Parser:load_file()]: Error parsing file: {e}")
        self.logger.info(f"[AUTOSAR_Parser:load_file()]: Loading of file was successful. returning self.file_content_tree object")
        return self.file_content_tree

    def get_value(self, elementPath, reload_file=False, uuid=None,mapping=None):
        """
        Return Text value of Target element at elementPath
        :param elementPath: path within arxml-file to target element; Format: Short-Names_of_elements_along_the_path.tag_of_element (e.g. components.component1.SHORT-NAME)
        :return: Str: Text value of target element
            None if Text value is "" or None or file path or elementPath is invalid
        """
        self.logger.info(f"[AUTOSAR_Parser:get_value()]: attemting to get value at {elementPath} in file at {self.file_path}")
        #get value from arxml-Tree
        tgt_elem = self.find_elem(elementPath, reload_file=reload_file, uuid=uuid,mapping=mapping)
        if tgt_elem == None:
            self.logger.error(f"[AUTOSAR_Parser:get_value()]: Error: Element {elementPath} does not exist")
            return None
        tgt_val = tgt_elem.text
        if tgt_val.strip() == "" or tgt_val == None:
            self.logger.error(f"[AUTOSAR_Parser:get_value()]: Error: Element has no text value")
            return None
        self.logger.info(f"[AUTOSAR_Parser:get_value()]: found valid element. returning its value ({tgt_val})")
        return tgt_val

    def find_elem(self, elementPath, reload_file=False, uuid=None,mapping=None):
        """
                Load File and return Target Tree element at elementPath
                :param elementPath: path within arxml-file to target element; Format: Short-Names_of_elements_along_the_path.tag_names to item after last short name.tag_of_element (e.g. componentTypes.Component1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC.DATA-ELEMENT-REF)
                :param reload_file: Boolean. if True, the file at self.file_path will be reloaded into the parser, i.e. load_file() will be called
                :param root: root element from which the search begins
                :return: elementTree Object that matches element path
                    None if file path or elementPath is invalid or element not found
        """
        self.logger.info(f"[AUTOSAR_Parser:find_elem()]: attemting to get element at elementPath {elementPath}. reload_file = {reload_file}")

        if reload_file:
            self.logger.info(f"[AUTOSAR_Parser:find_elem()]:     reloading file at self.file_path = {self.file_path}")
            if self.load_file() == None:  #Update File
                self.logger.error(f"[AUTOSAR_Parser:find_elem()]: Could not load File at {self.file_path}")
                return None
        if elementPath == None or "":
            self.logger.error(f"[AUTOSAR_Parser:find_elem()]: Element path is None or empty String ")
            return None
        root = self.tree_root

        self.logger.info(f"[AUTOSAR_Parser:find_elem()]: input parameters are valid proceeding.")
        schema = root.tag.split("}")[0]+"}"

        search_list = [(root,elementPath)]

        #bfs throug xml tree
        while len(search_list) > 0:
            #get text value of next element "next_element" on path; if it is the last element on the path, check if any child tag fits next_element and return that child if true
            current_element, current_elementPath = search_list.pop(0)
            self.logger.info(f"[AUTOSAR_Parser:find_elem()]:    current_elem: {current_element.tag.split("}")[-1]}, path: {current_elementPath}")
            if current_elementPath == "": continue
            next_element = current_elementPath.split(".",1)[0]
            if len(current_elementPath.split(".",1)) > 1:
                current_elementPath = current_elementPath.split(".",1)[-1]
            else:#next_element is last entry in path -> must be a tag of a child of current element or a there will come a child with a child with tag=SHORT-Name with text value=next_element Else elementPath is invalid
                current_elementPath = ""
                for child in current_element:
                    
                    if child.tag.split("}")[-1] == next_element or child.find(f"[{schema}SHORT-NAME='{next_element}']"):
                        self.logger.info(f"[AUTOSAR_Parser:find_elem()]: found element. returning elementTree Object")
                        return child
                    else: 
                        search_list.append((child,next_element))
                continue
                
            #ckeck, if current_element has a child that has an AUTOSAR path address of value next_element and add it to seach list
            AUTOSAR_path_matches = current_element.findall(f"./*[{schema}SHORT-NAME='{next_element}']") #finds element that has a child with tag "SHORT-NAME" with text value "next_element"
            for AUTOSAR_path_match in AUTOSAR_path_matches: #bfs in all AUTOSAR path matches

                self.logger.info(f"[AUTOSAR_Parser:find_elem()]:         found AUTOSAR Path match: {next_element}")
                search_list = [(AUTOSAR_path_match,current_elementPath)]


            #if no AUTOSAR path match was found: check for tag path matches and add them to search list; if no tag path match was found: add all children to search list without shortening search path
            if not AUTOSAR_path_matches or len(AUTOSAR_path_matches) == 0:
                tag_path_matches = current_element.findall(f"./{schema}{next_element}")
                for tag_path_match in tag_path_matches: #bfs in all tag path matches
                        self.logger.info(f"[AUTOSAR_Parser:find_elem()]:         found Tag match: {next_element}")
                        search_list=[]
                        search_list.append((tag_path_match, current_elementPath))
                if not tag_path_matches or len(tag_path_matches) == 0:#case: no AUTOSAR path matches and no tag path matches -> bfs in all children that are not autosar adressable
                    self.logger.info(f"[AUTOSAR_Parser:find_elem()]:         found no match. expaning search to all subelements")
                    for child in current_element:
                        if child.find(f"./{schema}SHORT-NAME") == None:
                            search_list.append((child,f"{next_element}.{current_elementPath}"))
            
        if mapping == None or uuid == None:
            self.logger.error("[AUTOSAR_Parser:find_elem()]: element not found (search_list is empty)")        
            return None    
        # try to find element by provided uuid -> mapping file has outdated element path
        self.logger.debug(f"looking for element with UUID = {uuid}")
        find_elem_by_uuid = self.tree_root.find(f".//*[@UUID='{uuid}']")
        #print(f"find_elem_by_uuid = {find_elem_by_uuid}")
        if find_elem_by_uuid != None:
            self.logger.info(f"[AUTOSAR_Parser:find_elem()]: found Element by uuid and not by elementPath. Updating Element Path ")
            AUTOSAR_only_path = self.get_AUTOSAR_only_path(find_elem_by_uuid).replace("/",".")[1:]
            

            AUTOSAR_model = mapping["AUTOSAR"]
            
            for AUTOSAR_model_element in AUTOSAR_model:
                if AUTOSAR_model_element["parent_uuid"]==uuid:
                    xml_tag_path = AUTOSAR_model_element["elementPath"].split(".")[AUTOSAR_model_element["index"]:]
                    AUTOSAR_model_element["elementPath"]=f"{AUTOSAR_only_path}.{".".join(xml_tag_path)}"
                    AUTOSAR_model_element["index"]=len(AUTOSAR_only_path.split("."))
                    lookup_str = ""
                    for xml_tag in xml_tag_path[:-1]:   
                        lookup_str = f"{lookup_str}{schema}{xml_tag}."
                    lookup_str = f"{lookup_str}{schema}{xml_tag_path[-1]}"
                    return find_elem_by_uuid.find(f"./{lookup_str}")
        #if search_list is empty and no element was found
        self.logger.error("[AUTOSAR_Parser:find_elem()]: element not found in search list nor by uuid")        
        return None           

    def set_value(self, elementPath, value, mapping):
        """

        :param elementPath: path within arxml-file to target element; Format: Short-Names_of_elements_along_the_path.tags_to_element (e.g. components.component1.SHORT-NAME)
        :param value: value to which the target Element shall be changed
        :param mapping: content of mapping.json
        :return: True if value was changed correctly,
            Else False
        """
        self.logger.info(f"[AUTOSAR_Parser:set_value()]: attemting to set value = {value} to Element at {elementPath} at file {self.file_path}")
        #validate that Value is not None or ""
        if not value or value =="":
            self.logger.error("[AUTOSAR_Parser:set_value()]: Value is None and will not be set to tgt_elem['value']")
            return False
        
        #find Element
        tgt_elem = self.find_elem(elementPath)

        #set Elements value
        if tgt_elem == None:
            self.logger.error(f"[AUTOSAR_Parser:set_value()]: Error: Element {elementPath} does not exist")
            return False
        schema = tgt_elem.tag.split("}")[0]+"}"

        self.logger.info(f"[AUTOSAR_Parser:set_value()]: input parameters are valid. proceeding to set value...")

        if tgt_elem.tag == f"{schema}SHORT-NAME":  #element to set is a short name -> update all occurences of that short name in arxml_file
            AUTOSAR_only_path = self.get_AUTOSAR_only_path(self.parent_map.get(tgt_elem))
            new_AUTOSAR_only_path = AUTOSAR_only_path.split("/")
            new_AUTOSAR_only_path[-1]=value
            new_AUTOSAR_only_path = ".".join(new_AUTOSAR_only_path)[1:]
            if self.find_elem(new_AUTOSAR_only_path) != None: #there exists an element that has the same SHORT-NAME in the same Tree-Level
                self.logger.error(f"[AUTOSAR_Parser:set_value()]:    There is already an Element with Path {new_AUTOSAR_only_path}. The Element can therefore not be renamed to {value}")
                return False
            self.logger.info(f"[AUTOSAR_Parser:set_value()]:     target element is a short_name_tag at path {AUTOSAR_only_path}. All Occurences of that name in the file will be changed to the new name: {value}")
            path_occurences = self.tree_root.findall(f".//*[@DEST]")
            
            for path_occurence in path_occurences:
                splitted_ref = path_occurence.text.split("/")
                if path_occurence.text.startswith(AUTOSAR_only_path):
                    splitted_ref = [value if elem == tgt_elem.text else elem for elem in splitted_ref]
                    path_occurence.text = "/".join(splitted_ref)

            AUTOSAR_model = mapping["AUTOSAR"]
            AUTOSAR_only_element_path = AUTOSAR_only_path.replace("/",".")[1:]
            for AUTOSAR_model_element in AUTOSAR_model:
                if AUTOSAR_model_element["elementPath"].startswith(AUTOSAR_only_element_path):
                    splitted_ep = AUTOSAR_model_element["elementPath"].split(".")
                    splitted_ep = [value if elem == tgt_elem.text else elem for elem in splitted_ep]
                    AUTOSAR_model_element["elementPath"] = ".".join(splitted_ep)
                    AUTOSAR_model_element["lastModified"] = datetime.now().strftime("%d.%m.%Y")

            tgt_elem.text = value
        
        elif tgt_elem.attrib.get("DEST"):  # element to set is reference to another element -> shall only be set to another element of same type and not itself
            AUTOSAR_element_type = tgt_elem.attrib.get("DEST")
            converted_elementPath = value.replace("/",".")[1:]
            new_referenced_element = self.find_elem(converted_elementPath)
            self.logger.info(f"[AUTOSAR_Parser:set_value()]:     target element is reference to an element of type {AUTOSAR_element_type} and shall reference a new element at {value}. checking type compatibility")
            if new_referenced_element != None and new_referenced_element.tag == schema+AUTOSAR_element_type:  #new reference exists and is of same type as old one
                self.logger.info(f"[AUTOSAR_Parser:set_value()]:     type of new referenced element is valid")
                tgt_elem.text = value
            else:
                self.logger.error(f"[AUTOSAR_Parser:set_value()]: new reference {value} is invalid")
                return False

        elif tgt_elem.text == None or tgt_elem.text.strip() == "":
    
            self.logger.error("[AUTOSAR_Parser:set_value()]: cannot update value of non text element")
            return False
        else:
            self.logger.info(f"[AUTOSAR_Parser:set_value()]:     target element is of no special type. proceeding to change value")
            tgt_elem.text = value

        # save changes
        uri = schema[1:-1]
        ET.register_namespace('',uri)
        self.file_content_tree.write(self.file_path, encoding='UTF-8', xml_declaration=True, default_namespace=None, method='xml')
        self.logger.info(f"[AUTOSAR_Parser:set_value()]: value has been set successfully")
        return True
    
    def get_AUTOSAR_only_path(self,element):
        """
        generate AUTOSAR path without tag adressing that is used to address elements inside an arxml-file according to AUTOSAR-standard
        element must be uniquely addressable by AUTOSAR path
        :param element: element in elementTree
        :return: AUTOSAR path; None on error
        """
        self.logger.info(f"[AUTOSAR_Parser:get_AUTOSAR_only_path()]: attemting to get AUTOSAR_only_path of element")
        if element == None:
            self.logger.error("[AUTOSAR_Parser:get_AUTOSAR_only_path()]: provided element is None")
            return None
        schema = element.tag.split("}")[0]+"}"
        child = element.find(f"./{schema}SHORT-NAME")

        if child == None and False:
            self.logger.error("[AUTOSAR_Parser:get_AUTOSAR_only_path()]: provided element cannot be accessed by AUTOSAR_only_path as it has no child with tag=SHORT-NAME")
            return None
       
        self.logger.info(f"[AUTOSAR_Parser:get_AUTOSAR_only_path()]: input parameters are valid. Proceeding to generate path")
        #build AUTOSAR path
        AUTOSAR_only_path = ""
        current_element = element
        while current_element !=None:
            short_name_elem = current_element.find(f"./{schema}SHORT-NAME")
            if short_name_elem != None:
                short_name_text = short_name_elem.text.split("}")[-1]
                AUTOSAR_only_path = f"/{short_name_text}{AUTOSAR_only_path}"
            current_element = self.parent_map.get(current_element)

        #return AUTOSAR path
        self.logger.info(f"[AUTOSAR_Parser:get_AUTOSAR_only_path()]: path generation was successful. returning {AUTOSAR_only_path}")
        return AUTOSAR_only_path