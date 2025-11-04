import unittest
from metadata_manager import MetadataManager
from AUTOSAR_Parser import AUTOSAR_Parser
from file_parser import *
from main import GUI
from main import VersionControl

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import StringVar 
from tkinter import filedialog 
import customtkinter as ctk
import xml.etree.ElementTree as ET

class Test_GUI_popup_mapping_editor(unittest.TestCase):
    """
    Testcases:
        empty_json.json
        m2o_nvc
        o2o_ncv
    """
    def setUp(self):
        pass

    def test_GUI_popup_mapping_editor(self):
        print(f"TESTING: test_GUI_popup_mapping_editor")
        config_params = {
            "empty_json": "empty_json.json",
            "m2o_nvc": "mapping_many_to_one_No_value_change.json",
            "o2o_nvc": "mapping_one_to_one_No_value_change.json"
        }
        test_cases = [tc for tc,param in config_params.items()]
        test_case = test_cases[2]
        mapping_file_name = config_params[test_case]
        #for test_case, mapping_file_name in config_params.items():
        print(f"test_case: {test_case}")
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup(mapping_file_name=mapping_file_name)
        stub_root, frame = stub_frame()
        result = self.app.popup_mapping_editor(frame)
        assert(result == True)
        stub_root.mainloop()
        
        frame = None
        stub_root = None
        self.tearDown()

    def tearDown(self):
        self.fp_AUTOSAR = None
        self.fp_code = None
        self.fp_gerber = None
        self.fp_step = None
        self.fp_sysml = None
        self.vc = None
        self.mm = None
        self.app = None

        global_teardown(self.files)
        
        self.files = None

class Test_GUI_popup_conflict_manager(unittest.TestCase):
    """
    Testcases:
        invalid conflict list(None,wrong type)
        conflict list []
        conflict list many to one
        conflcit list one to one
    """
    def setUp(self):
        pass

    def test_GUI_popup_conflict_manager(self):
        print(f"TESTING: test_GUI_popup_conflict_manager")
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()

        conflict_list_m2o = [
            (self.mm.get_model_element("92019528-8c6c-11f0-af85-325096b39f47"),self.mm.get_mapped_domain_elements("92019528-8c6c-11f0-af85-325096b39f47"),"snd_Value_1_new"),
            (self.mm.get_model_element("9201976c-8c6c-11f0-a2c7-325096b39f47"),self.mm.get_mapped_domain_elements("9201976c-8c6c-11f0-a2c7-325096b39f47"),"new/path")
        ]
        conflict_list_m2o[0][1][1]["value"]="snd_Value_1_new"
        conflict_list_m2o[1][1][0]["value"]="new/path"

        conflict_list_o2o = [(self.mm.get_model_element("92019848-8c6c-11f0-849e-325096b39f47"),self.mm.get_mapped_domain_elements("92019848-8c6c-11f0-849e-325096b39f47"),"Component_1_new")]
        conflict_list_o2o[0][0]["value"]="Component_1_new"

        parameters = {
            "invalid_conflict_list_wrong_type":"wrong_type",
            "invalid_conflict_list_None":None,
            "conflict_list_empty":[],
            "conflict_list_m2o":conflict_list_m2o,
            "conflict_list_o2o":conflict_list_o2o
        }
    
        assertions = {
            "invalid_conflict_list_wrong_type": None,
            "invalid_conflict_list_None":None,
            "conflict_list_empty": None,
            "conflict_list_m2o": True,
            "conflict_list_o2o": True
        }

        test_cases = [tc for tc,param in parameters.items()]
        test_case = test_cases[4]
        conflict_list = parameters[test_case]
        #for test_case, conflict_list in parameters.items():
        print(f"test_case: {test_case}")
        stub_root, frame = stub_frame()
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()

        result = self.app.popup_conflict_manager(conflict_list=conflict_list, main_frame_conflict_manager=frame)
        assert(assertions[test_case]==result)
        stub_root.mainloop()
        self.tearDown()
        frame = None
        stub_root = None

    def tearDown(self):
        self.fp_AUTOSAR = None
        self.fp_code = None
        self.fp_gerber = None
        self.fp_step = None
        self.fp_sysml = None
        self.vc = None
        self.mm = None
        self.app = None
        global_teardown(self.files)
        
        self.files = None

class Test_GUI_select_file(unittest.TestCase):
    """
    Testcases:
        arxml
        normal file
        all other params none
    """
    def setUp(self):
        pass

    def test_GUI_select_file(self):
        print(f"TESTING: test_GUI_select_file")
        for i in range(3):
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
            stub_root, mapping_frame, strvar_path, strvar_value = stub_mapping_frame()
            
            self.app.select_file(model_type="domain",content_frame=mapping_frame,selected_domain_element_name=strvar_path,selected_domain_element_value=strvar_value)
            stub_root.mainloop()
            self.tearDown()
            stub_root=None
            mapping_frame=None
            strvar_path = None
            strvar_value = None
            

    def tearDown(self):
        self.fp_AUTOSAR = None
        self.fp_code = None
        self.fp_gerber = None
        self.fp_step = None
        self.fp_sysml = None
        self.vc = None
        self.mm = None
        self.app = None

        global_teardown(self.files)
        
        self.files = None

class Test_GUI_load_file_content(unittest.TestCase):
    """
    Testcases:
        arxml
        normal file
        all other params none
    """
    def setUp(self):
        pass

    def test_GUI_load_file_content(self):
        print(f"TESTING: Test_GUI_load_file_content")

        external_root, external_frame = stub_frame()
        text_widget = tk.Text(external_frame, wrap=tk.WORD)
        text_widget.grid(row=3,column=0)
        #external_root.mainloop()

        parameters = {
            "arxml":("./tests/testing_files/arxml_domain.arxml",external_frame,"strvar_path","strvar_value",None),
            "arxml_content_frame_none":("./tests/testing_files/arxml_domain.arxml",None,"strvar_path","strvar_value",None),
            "normal":("./tests/testing_files/normal_text_file.txt",external_frame,"strvar_path","strvar_value",None),
            "text_widget":("./tests/testing_files/normal_text_file.txt",None,None,None,text_widget),
            "none_strvar_arxml": ("./tests/testing_files/arxml_domain.arxml",external_frame,None,None,None),
            "filepath_normal_wrong": ("./tests/testing_files/normal_text_fierwle.txt",external_frame,"strvar_path","strvar_value",None),
            "filepath_text_widget_wrong": ("./tests/testing_files/normal_text_erfile.txt",None,"strvar_path","strvar_value",text_widget)
        }

        assertions = {
            "arxml": True,
            "arxml_content_frame_none":False,
            "normal": "normal text file",
            "text_widget": "normal text file",
            "none_strvar_arxml": False,
            "filepath_normal_wrong": False,
            "filepath_text_widget_wrong": False

        }

        for test_case,(file_path,content_frame,strvar_p,strvar_v,text_widget) in parameters.items():
            print(f"test_case: {test_case}")
            root, mapping_frame, strvar_path, strvar_value = stub_mapping_frame()
            if content_frame==None: mapping_frame = None
            if strvar_p == None: strvar_path = None
            if strvar_v == None: strvar_value = None
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
            result = self.app.load_file_content(file_path=file_path,content_frame=mapping_frame,selected_domain_element_name=strvar_path,selected_domain_element_value=strvar_value,text_widget=text_widget)
            assert(result == assertions[test_case])
            #root.mainloop()

            self.tearDown()
            root = None
            mapping_frame = None
            strvar_path = None
            strvar_value = None

    def tearDown(self):
        self.fp_AUTOSAR = None
        self.fp_code = None
        self.fp_gerber = None
        self.fp_step = None
        self.fp_sysml = None
        self.vc = None
        self.mm = None
        self.app = None

        global_teardown(self.files)
        
        self.files = None


class Test_GUI_generate_treeView_from_arxml(unittest.TestCase):
    """
    Testcases:
        arxml_domain with content frame leading to stub gui
        none for other params
    """
    def setUp(self):
        pass

    def test_GUI_generate_treeView_from_arxml(self):
        print(f"TESTING: test_GUI_generate_treeView_from_arxml")
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()

        parameters = {
            "valid": (True,self.fp_AUTOSAR,"strvar_name","strvar_value"),
            "content_frame_is_None":(None,self.fp_AUTOSAR,"strvar_name","strvar_value"),
            "Parser_is_None":(True,None,"strvar_name","strvar_value"),
            "selected_domain_element_name_is_None": (True,self.fp_AUTOSAR,None,"strvar_value"),
            "selected_domain_element_name_wrong_type": (True,self.fp_AUTOSAR,"WrongType","strvar_value"),
            "selected_domain_element_value_is_None": (True,self.fp_AUTOSAR,"strvar_name",None),
            "selected_domain_element_value_wrong_type":(True,self.fp_AUTOSAR,"strvar_name","WrongType"),
            "AUTSOAR_Parser_wrong_file":(True,self.fp_AUTOSAR,"strvar_name","strvar_value")
        }

        assertions = {
            "valid": "<AUTOSAR {http://www.w3.org/2001/XMLSchema-instance}schemaLocation=http://autosar.org/schema/r4.0 AUTOSAR_00046.xsd>",
            "content_frame_is_None": None,
            "Parser_is_None": None,
            "selected_domain_element_name_is_None": None,
            "selected_domain_element_name_wrong_type": None,
            "selected_domain_element_value_is_None": None,
            "selected_domain_element_value_wrong_type": None,
            "AUTSOAR_Parser_wrong_file": None
        }

        

        for test_case,(content_frame,AUTOSAR_Parser,strvar_n,strvar_v) in parameters.items():
            
            print(f"test_case: {test_case}")
            root, stub_content_frame, strvar_name, strvar_value = stub_mapping_frame()
            
            if strvar_n != "strvar_name": strvar_name = strvar_n
            if strvar_v != "strvar_value": strvar_value = strvar_v
           
            if content_frame == None: stub_content_frame=None
            
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
            if test_case == "AUTSOAR_Parser_wrong_file": 
                AUTOSAR_Parser.file_path=None
                AUTOSAR_Parser.tree_root=None
            result = self.app.generate_treeView_from_arxml(content_frame=stub_content_frame, 
                                                           AUTOSAR_Parser=AUTOSAR_Parser,
                                                           selected_domain_element_name=strvar_name,
                                                           selected_domain_element_value=strvar_value)
            if result: print(f"result: {result.item(result.get_children()[0],"text")}")
            print(f"assert: {assertions[test_case]}")
            if not result: assert(result == assertions[test_case])
            else: 
                assert(result.item(result.get_children()[0],"text") == assertions[test_case])
            #root.mainloop

            self.tearDown()

    def tearDown(self):
        self.fp_AUTOSAR = None
        self.fp_code = None
        self.fp_gerber = None
        self.fp_step = None
        self.fp_sysml = None
        self.vc = None
        self.mm = None
        self.app = None

        global_teardown(self.files)
        
        self.files = None
    

class Test_GUI_generate_tv_element_full_name(unittest.TestCase):
    """
    Testcases:
        shortname   attrib  text
        alle Kombis
        None als element
    """

    def test_GUI_generate_tv_element_full_name(self):
        print(f"TESTING: test_GUI_generate_tv_element_full_name")

        xml_file = "./tests/testing_files/testing_xml.xml"
        tree = ET.parse(xml_file)
        root = tree.getroot()

        self.app = None

        parameters = {
            "None_as_element":None,
            "000":root[0],
            "001":root[1],
            "010":root[2],
            "011":root[3],
            "100":root[4],
            "101":root[5],
            "110":root[6],
            "111":root[7],
        }
    
        assertions = {
            "None_as_element": None,
            "000":'<elem_000>',
            "001":'(sn_001)<elem_001>',
            "010":'<elem_010>010</elem_010>',
            "011":'(sn_011)<elem_011>011</elem_011>',
            "100":'<elem_100 attr1=attr_100_1,attr2=attr_100_2>',
            "101":'(sn_101)<elem_101 attr1=attr_101_1>',
            "110":'<elem_110 attr1=attr_110_1,attr2=attr_110_2>110</elem_110>',
            "111":'(sn_111)<elem_111 attr1=attr_111_1>111</elem_111>'
        }

        for test_case, xml_elem in parameters.items():
             print(f"test_case: {test_case}")
             self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
             result = self.app.generate_tv_element_full_name(xml_elem)
             print(f"result: {result}")
             assert(result == assertions[test_case])
             self.tearDown()



    def setUp(self):
        pass



    def tearDown(self):
        self.fp_AUTOSAR = None
        self.fp_code = None
        self.fp_gerber = None
        self.fp_step = None
        self.fp_sysml = None
        self.vc = None
        self.mm = None
        self.app = None

        global_teardown(self.files)
        
        self.files = None
    

class Test_GUI_get_tv_text_value(unittest.TestCase):
    """
    Testcases:
        shortname   attrib  text
        alle Kombis
        None als element
        invalider String
    """
    def setUp(self):
        pass

    def test_GUI_get_tv_text_value(self):
        print(f"TESTING: test_GUI_get_tv_text_value")
        parameters = {
            "None_as_element": None,
            "empty_str_as_element":"",
            "invalid_string":"invalid!!!",
            "000":'<elem_000>',
            "001":'(sn_001)<elem_001>',
            "010":'<elem_010>010</elem_010>',
            "011":'(sn_011)<elem_011>011</elem_011>',
            "100":'<elem_100 attr1="attr_100_1",attr_2="attr_100_2">',
            "101":'(sn_101)<elem_101 attr1="attr_101_1",attr_2="attr_101_2">',
            "110":'<elem_110 attr1="attr_110_1",attr_2="attr_110_2">110</elem_110>',
            "111":'(sn_111)<elem_111 attr1="attr_111_1",attr_2="attr_111_2">111</elem_111>'
        }

        assertions = {
            "None_as_element": None,
            "empty_str_as_element":None,
            "invalid_string":None,
            "000":None,
            "001":None,
            "010":'010',
            "011":"011",
            "100":None,
            "101":None,
            "110":"110",
            "111":"111"
        }

        for test_case, full_name in parameters.items():
             print(f"test_case: {test_case}")
             self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
             result = self.app.get_tv_text_value(full_name)
             assert(result == assertions[test_case])
             self.tearDown()

    def tearDown(self):
        self.fp_AUTOSAR = None
        self.fp_code = None
        self.fp_gerber = None
        self.fp_step = None
        self.fp_sysml = None
        self.vc = None
        self.mm = None
        self.app = None

        global_teardown(self.files)
        
        self.files = None

class Test_GUI_get_tv_tag_value(unittest.TestCase):
    """
    Testcases:
        shortname   attrib  text
        alle Kombis
        None als element
    """
    def setUp(self):
        pass

    def test_GUI_get_tv_tag_value(self):
        print(f"TESTING: test_GUI_get_tv_tag_value")
        parameters = {
            "None_as_element": None,
            "empty_str_as_element":"",
            "invalid_string":"invalid!!!",
            "000":'<elem_000>',
            "001":'(sn_001)<elem_001>',
            "010":'<elem_010>010</elem_010>',
            "011":'(sn_011)<elem_011>011</elem_011>',
            "100":'<elem_100 attr1="attr_100_1",attr_2="attr_100_2">',
            "101":'(sn_101)<elem_101 attr1="attr_101_1",attr_2="attr_101_2">',
            "110":'<elem_110 attr1="attr_110_1",attr_2="attr_110_2">110</elem_110>',
            "111":'(sn_111)<elem_111 attr1="attr_111_1",attr_2="attr_111_2">111</elem_111>'
        }

        assertions = {
            "None_as_element": None,
            "empty_str_as_element":None,
            "invalid_string":None,
            "000":"elem_000",
            "001":"elem_001",
            "010":"elem_010",
            "011":"elem_011",
            "100":"elem_100",
            "101":"elem_101",
            "110":"elem_110",
            "111":"elem_111"
        }

        for test_case, full_name in parameters.items():
             print(f"test_case: {test_case}")
             self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
             result = self.app.get_tv_tag_value(full_name)
             assert(result == assertions[test_case])
             self.tearDown()

    def tearDown(self):
        self.fp_AUTOSAR = None
        self.fp_code = None
        self.fp_gerber = None
        self.fp_step = None
        self.fp_sysml = None
        self.vc = None
        self.mm = None
        self.app = None

        global_teardown(self.files)
        
        self.files = None

class Test_GUI_get_tv_AUTOSAR_path_value(unittest.TestCase):
    """
    Testcases:
        shortname   attrib  text
        alle Kombis
        None als element
    """
    def setUp(self):
        pass

    def test_GUI_get_tv_AUTOSAR_path_value(self):
        print(f"TESTING: test_GUI_get_tv_AUTOSAR_path_value")
        parameters = {
            "None_as_element": None,
            "empty_str_as_element":"",
            "invalid_string":"invalid!!!",
            "000":'<elem_000>',
            "001":'(sn_001)<elem_001>',
            "010":'<elem_010>010</elem_010>',
            "011":'(sn_011)<elem_011>011</elem_011>',
            "100":'<elem_100 attr1="attr_100_1",attr_2="attr_100_2">',
            "101":'(sn_101)<elem_101 attr1="attr_101_1",attr_2="attr_101_2">',
            "110":'<elem_110 attr1="attr_110_1",attr_2="attr_110_2">110</elem_110>',
            "111":'(sn_111)<elem_111 attr1="attr_111_1",attr_2="attr_111_2">111</elem_111>'
        }

        assertions = {
            "None_as_element": None,
            "empty_str_as_element":None,
            "invalid_string":None,
            "000":None,
            "001":"sn_001",
            "010":None,
            "011":"sn_011",
            "100":None,
            "101":"sn_101",
            "110":None,
            "111":"sn_111"
            }

        for test_case, full_name in parameters.items():
                print(f"test_case: {test_case}")
                self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
                result = self.app.get_tv_AUTOSAR_path_value(full_name)
                assert(result == assertions[test_case])
                self.tearDown()

    def tearDown(self):
        self.fp_AUTOSAR = None
        self.fp_code = None
        self.fp_gerber = None
        self.fp_step = None
        self.fp_sysml = None
        self.vc = None
        self.mm = None
        self.app = None

        global_teardown(self.files)
        
        self.files = None

class Test_GUI_get_tv_elementPath(unittest.TestCase):
    """
    Testcases:
        None parameter
        tv_item:
            no text value
            AUTOSAR only (e.g. Port oder SWC)
            inside AUTOSAR only
    """
    def setUp(self):
        pass

    def test_GUI_get_tv_elementPath(self):
        print(f"TESTING: test_GUI_get_tv_elementPath")
        
        root, content_frame, strvar_name , strvar_value = stub_mapping_frame()
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
        tv = self.app.generate_treeView_from_arxml(content_frame=content_frame,
                                                   AUTOSAR_Parser=self.fp_AUTOSAR,
                                                   selected_domain_element_name=strvar_name,
                                                   selected_domain_element_value=strvar_value)

        parameters = {
            "no_text_value":[0,1,1,0,1,0],
            "root":[0],
            "AUTOSAR_Only":[0,1,1,0,1,0,0],
            "AUTOSAR_and_Tags":[0,1,1,0,1,0,1,0,0],
            "tv_none":[0,1,1,0,1,0,0],
            "item_none":[0,1,1,0,1,0,0]
        }
    
        assertions = {
            "no_text_value": None,
            "root": None,
            "AUTOSAR_Only": "ComponentTypes.Component_1.snd_Value_1.SHORT-NAME",
            "AUTOSAR_and_Tags": "ComponentTypes.Component_1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC.DATA-ELEMENT-REF",
            "tv_none":None,
            "item_none":None
        }
    
        for test_case, childpath in parameters.items():
            print(f"test_case: {test_case}")
            root = tv.get_children()[0]
            tv_item = root
            for index in childpath:
                tv_item = tv.get_children(tv_item)[index]
            
            if test_case == "item_none": tv_item = None
            result = self.app.get_tv_elementPath(tv=tv,tv_item=tv_item)
            if test_case=="tv_none": result = self.app.get_tv_elementPath(tv=None, tv_item=tv_item)
            print(f"result: {result}")
            assert(result == assertions[test_case])
        
        self.tearDown()



    def tearDown(self):
        self.fp_AUTOSAR = None
        self.fp_code = None
        self.fp_gerber = None
        self.fp_step = None
        self.fp_sysml = None
        self.vc = None
        self.mm = None
        self.app = None

        global_teardown(self.files)
        
        self.files = None

class Test_GUI_set_map_frame_domain_value_entry(unittest.TestCase):
    """
    Testcases:
        None cases
        selection without text value
        selection with text value
    """
    def setUp(self):
        pass

    def test_GUI_set_map_frame_domain_value_entry(self):
        print(f"TESTING: test_GUI_set_map_frame_domain_value_entry")
        root, content_frame, strvar_name , strvar_value = stub_mapping_frame()
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
        tv = self.app.generate_treeView_from_arxml(content_frame=content_frame,
                                                   AUTOSAR_Parser=self.fp_AUTOSAR,
                                                   selected_domain_element_name=strvar_name,
                                                   selected_domain_element_value=strvar_value)
        root.mainloop()

    def tearDown(self):
        self.fp_AUTOSAR = None
        self.fp_code = None
        self.fp_gerber = None
        self.fp_step = None
        self.fp_sysml = None
        self.vc = None
        self.mm = None
        self.app = None

        global_teardown(self.files)
        
        self.files = None

class Test_GUI_generate_conflict_entry_frame(unittest.TestCase):
    """
    Testcases:
        None cases
        conflict o2o
        conflict m2o
    """
    def setUp(self):
        pass

    def test_GUI_generate_conflict_entry_frame(self):
        print(f"TESTING: test_GUI_generate_conflict_entry_frame")
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()

        conflict_m2o_1 = (self.mm.get_model_element("92019528-8c6c-11f0-af85-325096b39f47"),self.mm.get_mapped_domain_elements("92019528-8c6c-11f0-af85-325096b39f47"),"snd_Value_1_new")
        conflict_m2o_1[1][1]["value"] = "snd_Value_1_new"
        
        conflict_m2o_2 = (self.mm.get_model_element("92019528-8c6c-11f0-af85-325096b39f47"),self.mm.get_mapped_domain_elements("92019528-8c6c-11f0-af85-325096b39f47"),"snd_Value_1")
        conflict_m2o_2[1][2]["value"] = "snd_Value_1_new"

        conflict_o2o_1 = (self.mm.get_model_element("92019848-8c6c-11f0-849e-325096b39f47"),self.mm.get_mapped_domain_elements("92019848-8c6c-11f0-849e-325096b39f47"),"Component_1_new")
        conflict_o2o_1[0]["value"]="Component_1_new"
        
        conflict_o2o_2 = (self.mm.get_model_element("92019848-8c6c-11f0-849e-325096b39f47"),self.mm.get_mapped_domain_elements("92019848-8c6c-11f0-849e-325096b39f47"),"Component_1")
        conflict_o2o_2[1][0]["value"]="Component_1_new"

        parameters = {
            "invalid_conflict_wrong_type":"wrong_type",
            "invalid_conflict_None":None,
            "conflict_m2o_1":conflict_m2o_1,
            "conflict_o2o_1":conflict_o2o_1,
            "conflict_m2o_2":conflict_m2o_2,
            "conflict_o2o_2":conflict_o2o_2
        }
    
        assertions = {
            "invalid_conflict_wrong_type": (None,0),#number is len of selection list
            "invalid_conflict_None":(None,0),
            "conflict_m2o_1": (True,4),
            "conflict_o2o_1": (True,2),
            "conflict_m2o_2": (True,4),
            "conflict_o2o_2": (True,2)
        }
        #test_cases = [tc for tc,param in parameters.items()]
        #test_case = test_cases[5]
        #conflict = parameters[test_case]
        for test_case, conflict in parameters.items():
            print(f"test_case: {test_case}")
            selection_list = []
            stub_root, frame = stub_frame()
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()

            result = self.app.generate_conflict_entry_frame(conflict=conflict, main_frame_conflict_manager=frame, selection_list=selection_list)
            if not result: assert(assertions[test_case][0]==result)
            else: result.grid()
            assert(len(selection_list) == assertions[test_case][1])
            #stub_root.mainloop()
            self.tearDown()
            frame = None
            stub_root = None

    def tearDown(self):
        self.fp_AUTOSAR = None
        self.fp_code = None
        self.fp_gerber = None
        self.fp_step = None
        self.fp_sysml = None
        self.vc = None
        self.mm = None
        self.app = None

        global_teardown(self.files)
        
        self.files = None

class Test_GUI_generate_mapping_entry_frame(unittest.TestCase):
    """
    Testcases:
        None cases
        mapping o2o
        mapping m2o
    """
    def setUp(self):
        pass

    def test_GUI_generate_mapping_entry_frame(self):
        print(f"TESTING: test_GUI_generate_mapping_entry_frame")
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
        mappings = self.mm.get_Mappings_elements()
        mapping_m2o = mappings[0]
        mapping_o2o = mappings[-1]

        parameters = {
            "mapping_wrong_type":"wrong_type",
            "mapping_is_None":None,
            "mapping_m2o":mapping_m2o,
            "mapping_o2o":mapping_o2o
        }
    
        assertions = {
             "mapping_wrong_type":None,
            "mapping_is_None":None,
            "mapping_m2o":True,
            "mapping_o2o":True
        }

        #test_cases = [tc for tc,param in parameters.items()]
        #test_case = test_cases[3]
        #mapping = parameters[test_case]
        for test_case, mapping in parameters.items():
            
            print(f"test_case: {test_case}")
            stub_root, frame = stub_frame()
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()

            result = self.app.generate_mapping_entry_frame(mapping=mapping, main_frame_mapping_editor=frame)
            if not result: assert(assertions[test_case]==result)
            else: result.grid()
            #stub_root.mainloop()
            self.tearDown()
            frame = None
            stub_root = None

    def tearDown(self):
        self.fp_AUTOSAR = None
        self.fp_code = None
        self.fp_gerber = None
        self.fp_step = None
        self.fp_sysml = None
        self.vc = None
        self.mm = None
        self.app = None

        global_teardown(self.files)
        
        self.files = None

class Test_GUI_generate_change_log_element_frame(unittest.TestCase):
    def setUp(self):
        pass

    def test_GUI_generate_change_log_element_frame(self):
        print(f"TESTING: test_GUI_generate_change_log_element_frame")
        element =  [{
            "n_change": 0,
            "timestamp": "2025-10-11 14:38:06",
            "value": "APPLICATION-SW-COMPONENT-TYPEll",
            "changed_by": "Updated by consistency Management"
        }]
        uuid = "c86a52f2-8ccc-11f0-aab3-325096b39f47"

        parameters = {
            "element_None":(None,uuid),
            "uuid_None":(element,None),
            "frame_None":(element,uuid),
            "valid":(element,uuid),
        }
    
        assertions = {
            "element_None": False,
            "uuid_None":False,
            "frame_None":False,
            "valid":True
        }

        #test_cases = [tc for tc,param in parameters.items()]
        #test_case = test_cases[0]
        #change_log_element,uuid = parameters[test_case]
        for test_case, (change_log_element,uuid) in parameters.items():
            
            print(f"test_case: {test_case}")
            stub_root, frame = stub_frame()
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
            if test_case == "frame_None": frame =None
            result = self.app.generate_change_log_element_frame(changelog_element=change_log_element,changelog_element_uuid=uuid,main_frame_change_log_viewer=frame)
            if not result: assert(assertions[test_case]==result)
            else: result.grid()
            #stub_root.mainloop()
            self.tearDown()
            frame = None
            stub_root = None

    def tearDown(self):
        self.fp_AUTOSAR = None
        self.fp_code = None
        self.fp_gerber = None
        self.fp_step = None
        self.fp_sysml = None
        self.vc = None
        self.mm = None
        self.app = None

        global_teardown(self.files)
        
        self.files = None

class Test_GUI_popup_change_log(unittest.TestCase):
    def setUp(self):
        pass

    def test_GUI_popup_change_log(self):
        print(f"TESTING: test_GUI_popup_change_log")
        config_params = {
            "empty_json": "change_log_empty.json",
            "normal": "change_log.json"
        }
        test_cases = [tc for tc,param in config_params.items()]
        test_case = test_cases[1]
        changelog_file_name = config_params[test_case]
        #for test_case, mapping_file_name in config_params.items():
        print(f"test_case: {test_case}")
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup(change_log_file_name=changelog_file_name)
        stub_root, frame = stub_frame()
        result = self.app.popup_change_log(frame)
        assert(result == True)
        stub_root.mainloop()
        
        frame = None
        stub_root = None
        self.tearDown()

    def tearDown(self):
        self.fp_AUTOSAR = None
        self.fp_code = None
        self.fp_gerber = None
        self.fp_step = None
        self.fp_sysml = None
        self.vc = None
        self.mm = None
        self.app = None

        global_teardown(self.files)
        
        self.files = None


def global_setup(sysml_file_name=None,gerber_file_name=None,AUTOSAR_file_name=None, code_file_name=None, step_file_Name=None, testing_file_path=None, backup_file_path=None, mapping_file_name=None,change_log_file_name=None):
    
    DEFAULT_CONFIG_FILE = "./config/default_config.json" 
    DEFAULT_CONFIG = load_config(DEFAULT_CONFIG_FILE)

    if not testing_file_path: testing_file_path = "./tests/testing_files/"
    if not backup_file_path: backup_file_path = "./tests/testing_files/backup/"
    if not sysml_file_name: sysml_file_name = "sysml_file.sysml"
    if not gerber_file_name: gerber_file_name = "gerber_domain.gbrjob"
    if not AUTOSAR_file_name: AUTOSAR_file_name = "arxml_domain.arxml"
    if not code_file_name: code_file_name = "code_domain_m2o_nvc.py"
    if not step_file_Name: step_file_Name = ""
    if not mapping_file_name: mapping_file_name = "mapping_many_to_one_no_value_change.json"
    if not change_log_file_name: change_log_file_name = "change_log_empty.json"

    files = {
            "sysml" : sysml_file_name,
            "AUTOSAR" : AUTOSAR_file_name,
            "gerber" : gerber_file_name,
            "code" : code_file_name,
            "step" : step_file_Name,
            "mapping" : mapping_file_name,
            "change_log":change_log_file_name
        }
    

    fp_sysml = SysmlParser(config=DEFAULT_CONFIG, sysml_path=f"{testing_file_path}{files["sysml"]}")
    fp_AUTOSAR = AUTOSAR_Parser(f"{testing_file_path}{files["AUTOSAR"]}")
    fp_gerber = GerberParser(f"{testing_file_path}{files["gerber"]}")
    fp_code = CodeParser(f"{testing_file_path}{files["step"]}")
    fp_step = StepParser(f"{testing_file_path}{files["code"]}")

    vc = VersionControl(config=DEFAULT_CONFIG)

    mm = MetadataManager(config=DEFAULT_CONFIG,
                                versioncontrol=None,
                                gerberparser=fp_gerber,
                                stepparser=fp_step,
                                codeparser=fp_code,
                                AUTOSARparser=fp_AUTOSAR,
                                sysmlparser=fp_sysml,
                                default_sysml_element_write_prio=1)
    
    mm.mapping_file_path = f"{testing_file_path}{files["mapping"]}"
    mm.change_log_path = f"{testing_file_path}{files["change_log"]}"
    
    app = GUI(config=DEFAULT_CONFIG,versioncontrol=vc,metadatamanager=mm)
    mm.app = app

    return fp_AUTOSAR, fp_code, fp_gerber, fp_step, fp_sysml, mm, app, vc, files

def global_teardown(files):

    if not files: return

    testing_file_path = "./tests/testing_files/"
    backup_file_path = "./tests/testing_files/backup/"
    for file_name in files.values():
            if file_name == "": continue
            try:
                with open(f"{backup_file_path}{file_name}", "r") as src, open(f"{testing_file_path}{file_name}", "w") as dest:
                    dest.write(src.read())
            except Exception:
                print(f"error restoring {file_name} at {backup_file_path}{file_name} from src {testing_file_path}{file_name}")

def stub_mapping_frame():
    root = ctk.CTk()
    root.title("stub mapping frame")
    root.geometry("1000x1000")
    main_frame = ctk.CTkFrame(root, fg_color="lightgrey",height=1000,width=1000)
    content_frame = ctk.CTkScrollableFrame(main_frame, fg_color="lightgrey",height=1000,width=800)
    model_element_path = StringVar(value="")
    model_element_value = StringVar(value="")

    entry_model_element_path = ctk.CTkEntry(main_frame,textvariable=model_element_path)
    entry_model_element_value = ctk.CTkEntry(main_frame,textvariable=model_element_value)
    main_frame.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")
    content_frame.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")
    entry_model_element_path.grid(row=1, column=0, padx=3, pady=3, sticky="nsew")
    entry_model_element_value.grid(row=2, column=0, padx=3, pady=3, sticky="nsew")

    return root, content_frame,model_element_path,model_element_value

def stub_frame():

    root = ctk.CTk()
    root.title("stub frame")
    root.geometry("1500x1000")
    main_frame = ctk.CTkFrame(root, fg_color="lightgrey")
    content_frame = ctk.CTkScrollableFrame(main_frame, fg_color="lightgrey",width=1400, height=1000)
    
    main_frame.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")
    content_frame.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")
    
    return root, content_frame
    
#Source: https://stackoverflow.com/questions/5360833/how-do-i-run-multiple-classes-in-a-single-test-suite-in-python-using-unit-testin
def run_tests():
    GUI_test_cases = [#Test_GUI_popup_mapping_editor,               #done
                      #Test_GUI_popup_conflict_manager,             #done
                      #Test_GUI_select_file,                        #done
                      # Test_GUI_load_file_content,                  #done
                      # Test_GUI_generate_treeView_from_arxml,      #done
                      # Test_GUI_generate_tv_element_full_name,      #done
                      # Test_GUI_get_tv_text_value,                  #done
                      # Test_GUI_get_tv_tag_value,                   #done
                      # Test_GUI_get_tv_AUTOSAR_path_value,          #done
                      # Test_GUI_get_tv_elementPath,                 #done
                      #Test_GUI_set_map_frame_domain_value_entry,   #done
                      #Test_GUI_generate_conflict_entry_frame,      #done
                      #Test_GUI_generate_mapping_entry_frame        #done
                      # Test_GUI_generate_change_log_element_frame,  #done
                      #Test_GUI_popup_change_log                    #done
                      ]
    loader = unittest.TestLoader()

    suites_list = []

    for test_class in GUI_test_cases:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    AUTOSAR_Parser_test_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(AUTOSAR_Parser_test_suite)

if __name__ == '__main__':
    result = run_tests()