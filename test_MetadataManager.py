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

"""
UUIDS for mapping test files
92019528-8c6c-11f0-af85-325096b39f47
9201976c-8c6c-11f0-a2c7-325096b39f47
92019848-8c6c-11f0-849e-325096b39f47
920198a2-8c6c-11f0-b021-325096b39f47
920198e8-8c6c-11f0-9b70-325096b39f47
9201992e-8c6c-11f0-b985-325096b39f47
9201996a-8c6c-11f0-a611-325096b39f47
920199b0-8c6c-11f0-8d9d-325096b39f47
920199ec-8c6c-11f0-bb23-325096b39f47
92019a32-8c6c-11f0-958a-325096b39f47

c86a513a-8ccc-11f0-91ae-325096b39f47
c86a52f2-8ccc-11f0-aab3-325096b39f47
c86a5356-8ccc-11f0-abbc-325096b39f47
c86a53a6-8ccc-11f0-a3aa-325096b39f47
c86a53e2-8ccc-11f0-a7b6-325096b39f47
c86a5428-8ccc-11f0-b619-325096b39f47
c86a5464-8ccc-11f0-b9e4-325096b39f47
c86a54a0-8ccc-11f0-a3cd-325096b39f47
c86a54dc-8ccc-11f0-871b-325096b39f47
c86a5518-8ccc-11f0-a012-325096b39f47
"""

class Test_MetadataManager_update_sysml_model(unittest.TestCase):
    """
    Testcases:
    m2o_nvc
    m2o_vc
    o2o_nvc
    o2o_vc
    """
    def setUp(self):
        pass
    
    def test_MetadataManager_update_sysml_model(self):
        print("TESTING: test_MetadataManager_update_sysml_model")
        setup_parameters = {
            "m2o_nvc":("code_domain_m2o_nvc.py","mapping_many_to_one_no_value_change.json"),
            "m2o_vc":("code_domain_m2o_vc.py","mapping_many_to_one_value_changed.json"),
            "o2o_nvc":(None,"mapping_one_to_one_no_value_change.json"),
            "o2o_vc":(None,"mapping_one_to_one_value_changed.json")
        }

        test_cases = [
            "m2o_nvc",
            "m2o_vc",
            "o2o_nvc",
            "o2o_vc"
        ]
        test_case = test_cases[3]

        code_file_name = setup_parameters[test_case][0]
        mapping_file_name = setup_parameters[test_case][1]
        print(f"...with {test_case}")
        
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup(code_file_name=code_file_name, mapping_file_name=mapping_file_name)
        self.mm.update_sysml_model()
        self.app.root.mainloop()
        #assertion: no popup,popup,no popup,popup
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

class Test_MetadataManager_manager_consistency(unittest.TestCase):
    """
    Testcases:
        m2o_nvc
        m2o_vc
        o2o_nvc
        o2o_vc
    """
    def setUp(self):
        pass
        
    def test_MetadataManager_manager_consistency(self):
        print("TESTING: test_MetadataManager_manage_consistency")
        setup_parameters = {
            "m2o_nvc":("code_domain_m2o_nvc.py","mapping_many_to_one_no_value_change.json"),
            "m2o_vc":("code_domain_m2o_vc.py","mapping_many_to_one_value_changed.json"),
            "o2o_nvc":(None,"mapping_one_to_one_no_value_change.json"),
            "o2o_vc":(None,"mapping_one_to_one_value_changed.json")
        }

        test_cases = [
            "m2o_nvc",
            "m2o_vc",
            "o2o_nvc",
            "o2o_vc"
        ]
        test_case = test_cases[3]
        print(f"...with {test_case}")
        code_file_name = setup_parameters[test_case][0]
        mapping_file_name = setup_parameters[test_case][1]
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup(code_file_name=code_file_name, mapping_file_name=mapping_file_name)
        self.mm.manage_consistency()
        self.app.root.mainloop()
        #assertion: no popup,popup,nopopup,popup
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

class Test_MetadataManager_apply_value_changes_to_mapping(unittest.TestCase):
    """
    testcases:
        None as selection_list
        [] as selection_list
        selection_list or list items of wrong type
        nonexistent uuid in tuple
        valid selection_list(min 2 elements)
    """
    def setUp(self):
        pass

    def test_MetadataManager_apply_value_changes_to_mapping(self):
        print("TESTING: test_MetadataManager_apply_value_changes_to_mapping")        
        parameters = {
            "invalid_mapping_file":[(("9201996a-8c6c-11f0-a611-325096b39f47","42"),0)],
            "None":None,
            "[]":[],
            "wrong_type_list":"wrong_type",
            "wrong_type_elem":["wrong_type"],
            "nonexistent uuid":[(("abcdefg","42"),1)],
            "valid":[(("9201996a-8c6c-11f0-a611-325096b39f47","42"),0),
                     (("920199b0-8c6c-11f0-8d9d-325096b39f47","34"),1),
                     (("920198a2-8c6c-11f0-b021-325096b39f47","33"),1),
                     (("92019848-8c6c-11f0-849e-325096b39f47","54"),1)
                    ]
        }
        
        assertions = {
            "invalid_mapping_file":False,
            "None":False,
            "[]":True,
            "wrong_type_list":False,
            "wrong_type_elem":False,
            "nonexistent uuid":False,
            "valid":True
        }

        for test_case, selection_list in parameters.items(): 
            print(f"... testcase: {test_case}")
            
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
            if test_case == "invalid_mapping_file": self.mm.mapping_file_path=""
            result = self.mm.apply_value_changes_to_mapping(selection_list=selection_list)
            assert(result == assertions[test_case])
            if result:
                for uuid,new_value in [selection_item for selection_item, selection in selection_list if selection == 1]:
                    assert(self.mm.get_model_element(uuid,models=None)["value"] == new_value)
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

class Test_MetadataManager_get_Mappings_elements(unittest.TestCase):
    """
    testcases:
        mapping.json without mappings entries
        valid mapping.json
    """
    def setUp(self):
        pass

    def test_MetadataManager_get_Mappings_elements(self):
        print("TESTING: test_MetadataManager_get_Mappings_elements")
        setup_parameters = {
            "empty_json" : "empty_json.json",
            "valid": None
        }
        assertions = {
            "empty_json" : (0,()),
            "valid": (7,("920199b0-8c6c-11f0-8d9d-325096b39f47","92019528-8c6c-11f0-af85-325096b39f47"))#len of list, uuid data in 1st element (src_uuid,tgt_uuid)
        }
    
        for test_case, mapping_file_name in setup_parameters.items():
            print(f"... testcase: {test_case}")
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup(mapping_file_name=mapping_file_name)
            mapping = mapping_file_name
            if mapping: mapping = load_json(self.mm.mapping_file_path)
            result = self.mm.get_Mappings_elements(mapping)
            n_mappings,uuids = assertions[test_case]
            assert(n_mappings==len(result))
            if n_mappings>0:
                assert(assertions[test_case][1] in [(mapping_tuple[2]["uuid"],mapping_tuple[1]["uuid"]) for mapping_tuple in result])
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

class Test_MetadataManager_remove_mapping(unittest.TestCase):
    """
    Testcases:
        invalid target_uuid ("",None,not in mapping.json)
        invalid source_uuid ("",None,not in mapping.json)
        valid uuids
    """
    def setUp(self):
        pass
        
    def test_MetadataManager_remove_mapping(self):
        print("TESTING: test_MetadataManager_remove_mapping")
        parameters = {
            "invalid_target_str":("invalid","92019848-8c6c-11f0-849e-325096b39f47"),
            "invalid_target_None":(None,"92019848-8c6c-11f0-849e-325096b39f47"),
            "invalid_target_empty_str":("","92019848-8c6c-11f0-849e-325096b39f47"),
            "invalid_source_str":("9201996a-8c6c-11f0-a611-325096b39f47","invalid"),
            "invalid_source_None":("9201996a-8c6c-11f0-a611-325096b39f47",None),
            "invalid_source_empty_str":("9201996a-8c6c-11f0-a611-325096b39f47",""),
            "valid_o2o":("9201996a-8c6c-11f0-a611-325096b39f47","92019848-8c6c-11f0-849e-325096b39f47"),
            "valid_m2o":("920198a2-8c6c-11f0-b021-325096b39f47","9201976c-8c6c-11f0-a2c7-325096b39f47")
        }
        assertions = {
            "invalid_target_str":False,
            "invalid_target_None":False,
            "invalid_target_empty_str":False,
            "invalid_source_str":False,
            "invalid_source_None":False,
            "invalid_source_empty_str":False,
            "valid_o2o":True,
            "valid_m2o":True
        }

        for test_case,(src_uuid,tgt_uuid) in parameters.items():
            print(f"... testcase: {test_case}")
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup(change_log_file_name="changelog_remove_mapping.json")
            result = self.mm.remove_mapping(tgt_uuid,src_uuid)
            assert(result == assertions[test_case])
            if result:
                assert([mapping_element for mapping_element,sysml_element,domain_element in self.mm.get_Mappings_elements() 
                        if mapping_element["sourceUUID"]==parameters[test_case][0] and 
                        mapping_element["targetUUID"] == parameters[test_case][1]] == [])#mappings element deleted
                print(f"domain_model: {self.mm.get_model_element(parameters[test_case][0])}")
                assert(self.mm.get_model_element(parameters[test_case][0]) == None)#domain model element deleted
                if test_case == "valid_o2o":
                    print(f"sysml_model:{self.mm.get_model_element(parameters[test_case][1])}")
                    assert(self.mm.get_model_element(parameters[test_case][1]) == None)#sysml element deleted
                elif test_case == "valid_m2o":
                    assert(self.mm.get_model_element(parameters[test_case][1]) != None)
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

class Test_MetadataManager_get_mapped_domain_elements(unittest.TestCase):
    """Testcases:
        invalid sysml_model_uuid ("",None,not in mapping.json)
        invalid models (list, empty dict)
        mapping ([])
        valid mapping
    """
    def setUp(self):
        pass

    def test_MetadataManager_get_mapped_domain_elements(self):
        print("TESTING: test_MetadataManager_get_mapped_domain_elements")
        
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
        
        
        mapping_content = load_json(self.mm.mapping_file_path)
        mappings = mapping_content["Mappings"]
        models = {model_name: model_elements for model_name, model_elements in mapping_content.items() if model_name != "Mappings"}
        empty_models = {}

        parameters = {
            "invalid_sysml_model_uuid_None":(None,None,None),
            "invalid_sysml_model_uuid_empty_str":("",None,None),
            "invalid_sysml_model_uuid_str":("NotInMapping",None,None),
            "invalid_models_list":("9201976c-8c6c-11f0-a2c7-325096b39f47",["model","model_1"],None),
            "invalid_models_empty":("9201976c-8c6c-11f0-a2c7-325096b39f47",empty_models,None),
            "invalid_mapping_wrong_type":("9201976c-8c6c-11f0-a2c7-325096b39f47",models,"wrong"),
            "mapping_empty":("9201976c-8c6c-11f0-a2c7-325096b39f47",models,[]),
            "valid_m2o":("9201976c-8c6c-11f0-a2c7-325096b39f47",None,mappings),
            "valid_o2o":("92019848-8c6c-11f0-849e-325096b39f47",None,None)
        }
        assertions = {
            "invalid_sysml_model_uuid_None": None,
            "invalid_sysml_model_uuid_empty_str": None,
            "invalid_sysml_model_uuid_str": (0,""),
            "invalid_models_list": None,
            "invalid_models_empty": (0,""),
            "invalid_mapping_wrong_type": None,
            "mapping_empty": (0,""),
            "valid_m2o": (3,"c86a53a6-8ccc-11f0-a3aa-325096b39f47"),#1st uuid
            "valid_o2o": (1,"9201996a-8c6c-11f0-a611-325096b39f47")
        }

        self.tearDown()

        for test_case,(sysml_model_element_uuid,models,mapping) in parameters.items():
            print(f"... testcase: {test_case}")
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
            result = self.mm.get_mapped_domain_elements(sysml_model_element_uuid,models,mapping)
            print(f"result:")

            if result== None: assert(result == assertions[test_case])
            else:
                for res in result: print(f"    Element: uuid: {res["uuid"]}; value: {res["value"]}")
                (n_elements,uuid) = assertions[test_case]
                assert(n_elements == len(result))
                if n_elements>0:
                    assert(uuid in [element["uuid"] for element in result])
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

class Test_MetadataManager_get_model_element(unittest.TestCase):
    """
    Testcases:
        invalid uuid (None, "", not in models)
        models (None, [], wrong type)
        valid with models as dict
        valid with models as list
    """
    def setUp(self):
        pass

    def test_MetadataManager_get_model_element(self):
        print("TESTING: test_MetadataManager_get_model_element")
        
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()

        mapping_content = load_json(self.mm.mapping_file_path)
        models = {model_name: model_elements for model_name, model_elements in mapping_content.items() if model_name != "Mappings"}
        sysml_model = mapping_content["SysMLv2"]
        parameters = {
            "invalid_uuid_None":(None,models),
            "invalid_uuid_str":("notInMapping",models),
            "invalid_uuid_empty_str":("",models),
            "invalid_models_wrong_type":("c86a53a6-8ccc-11f0-a3aa-325096b39f47","wrongType"),
            "models_empty":("c86a53a6-8ccc-11f0-a3aa-325096b39f47",[]),
            "models_None":("c86a53a6-8ccc-11f0-a3aa-325096b39f47",None),
            "valid_dict_domain":("c86a53a6-8ccc-11f0-a3aa-325096b39f47",models),
            "valid_list_sysml":("9201976c-8c6c-11f0-a2c7-325096b39f47",sysml_model)
        }
    
        assertions = {
            "invalid_uuid_None": None,
            "invalid_uuid_str": None,
            "invalid_uuid_empty_str": None,
            "invalid_models_wrong_type": None,
            "models_empty": None,
            "models_None": "c86a53a6-8ccc-11f0-a3aa-325096b39f47",
            "valid_dict_domain": "c86a53a6-8ccc-11f0-a3aa-325096b39f47",
            "valid_list_sysml": "9201976c-8c6c-11f0-a2c7-325096b39f47"
        }
        self.tearDown()

        for test_case, (uuid,models) in parameters.items():
            print(f"... testcase: {test_case}")
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
            result = self.mm.get_model_element(uuid,models)
            if not result: assert(result == assertions[test_case])
            else:
                print(f"result: {result["uuid"]}; assertion: {assertions[test_case]}")
                assert(result["uuid"]==assertions[test_case])
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

class Test_MetadataManager_get_max_write_prio_element(unittest.TestCase):
    """
    Testcases:
        model elements (None, [], wrong type, wrong element type)
        valid model_elements without ties
        valid model_elements with ties
    """
    def setUp(self):
        pass
        
    def test_MetadataManager_get_max_write_prio_element(self):
        print("TESTING: test_MetadataManager_get_max_write_prio_element")
        
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()

        models_no_ties = [
            self.mm.get_model_element("9201992e-8c6c-11f0-b985-325096b39f47"), #wp = 0
            self.mm.get_model_element("c86a52f2-8ccc-11f0-aab3-325096b39f47"), #wp = 20
            self.mm.get_model_element("920199b0-8c6c-11f0-8d9d-325096b39f47") #wp = 10
        ]
        models_ties = [
            self.mm.get_model_element("9201992e-8c6c-11f0-b985-325096b39f47"), #wp = 0
            self.mm.get_model_element("c86a52f2-8ccc-11f0-aab3-325096b39f47"), #wp = 20
            self.mm.get_model_element("c86a53a6-8ccc-11f0-a3aa-325096b39f47") #wp = 20
        ]
        
        parameters = {
             "invalid_model_None": None,
             "invalid_model_wrong_type":"wrong_type",
             "invalid_model_element_wrong_type": ["wrong_element_type"],
             "model_empty_list":[],
             "valid_with_ties": models_ties,
             "valid_without_ties": models_no_ties
         }   
    
        assertions = {
             "invalid_model_None": None,
             "invalid_model_wrong_type": None,
             "invalid_model_element_wrong_type": None,
             "model_empty_list": None,
             "valid_with_ties": "c86a52f2-8ccc-11f0-aab3-325096b39f47",
             "valid_without_ties":"c86a52f2-8ccc-11f0-aab3-325096b39f47"
         }  

        self.tearDown()

        for test_case, model_elements in parameters.items():
            print(f"... testcase: {test_case}")
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
            result = self.mm.get_max_write_prio_element(model_elements)
            if not result:
                assert(result == assertions[test_case])
            else:
                assert(result["uuid"] == assertions[test_case])
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

class Test_MetadataManager_value_conflict_exists(unittest.TestCase):
    """
    invalid sysml_element (None, no dict)
    invalid domain_elements (None, no list, list contains no dicts)
    domain_elements = []
    valid with value conflict
    valid without value conflict
    """
    def setUp(self):
        pass

    def test_MetadataManager_value_conflict_exists(self):
        print("TESTING: test_MetadataManager_value_conflict_exists")
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()

        sysml_element_no_vc = self.mm.get_model_element("9201976c-8c6c-11f0-a2c7-325096b39f47")
        model_elements_no_vc = self.mm.get_mapped_domain_elements("9201976c-8c6c-11f0-a2c7-325096b39f47")

        sysml_element_vc = self.mm.get_model_element("92019848-8c6c-11f0-849e-325096b39f47")
        model_elements_vc = self.mm.get_mapped_domain_elements("92019528-8c6c-11f0-af85-325096b39f47")

        parameters = {
            "invalid_sysml_element_None": (None,model_elements_no_vc),
            "invalid_sysml_element_wrong_type": ("wrong_type",model_elements_no_vc),
            "invalid_domain_model_elements_None": (sysml_element_no_vc,None),
            "invalid_domain_model_elements_wrong_type": (sysml_element_no_vc,"wrong_type"),
            "invalid_domain_model_elements_wrong_type_item": (sysml_element_no_vc,["wrong_type"]),
            "domain_model_elements_empty_list": (sysml_element_no_vc,[]),
            "valid_vc": (sysml_element_vc,model_elements_vc),
            "valid_nvc":(sysml_element_no_vc, model_elements_no_vc)
        }

        assertions = {
            "invalid_sysml_element_None": None,
            "invalid_sysml_element_wrong_type": None,
            "invalid_domain_model_elements_None": None,
            "invalid_domain_model_elements_wrong_type": None,
            "invalid_domain_model_elements_wrong_type_item": False,
            "domain_model_elements_empty_list": False,
            "valid_vc": True,
            "valid_nvc": False
        }

        self.tearDown()

        for test_case, (sysml_element,model_elements) in parameters.items():
            print(f"... testcase: {test_case}")
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
            result = self.mm.value_conflict_exists(sysml_element, model_elements)
            assert(result==assertions[test_case])
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

class Test_MetadataManager_update_change_log(unittest.TestCase):
    def setUp(self):
        pass

    def test_MetadataManager_update_change_log(self):
        print("TESTING: test_MetadataManager_update_change_log")
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()

        parameters = {
            "uuid_None": (None,"value","reason"),
            "value_None":("c86a53a6-8ccc-11f0-a3aa-325096b39f47",None,"reason"),
            "changed_by_invalid":("c86a53a6-8ccc-11f0-a3aa-325096b39f47","value",42),
            "valid_new_entry": ("NEWUUID","value","reason"),
            "valid_append_entry":("c86a53a6-8ccc-11f0-a3aa-325096b39f47","value","reason")
        }

        assertions = {
           "uuid_None": False,
            "value_None": False,
            "changed_by_invalid": False,
            "valid_new_entry": True,
            "valid_append_entry": True
        }

        self.tearDown()

        for test_case, (uuid,value,reason) in parameters.items():
            print(f"... testcase: {test_case}")
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
            result = self.mm.update_change_log(uuid,value,reason)
            assert(result==assertions[test_case])
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

class Test_MetadataManager_delete_change_log_element(unittest.TestCase):

    def setUp(self):
        pass

    def test_MetadataManager_delete_change_log_element(self):
        
        print("TESTING: test_MetadataManager_update_change_log")
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
        
        change_log_file = "change_log.json"
        parameters = {
            "None": None,
            "invalid uuid": "aef ",
            "valid":"c86a53a6-8ccc-11f0-a3aa-325096b39f47"
        }

        assertions = {
           "None": False,
            "invalid uuid": False,
            "valid": True
        }

        self.tearDown()

        for test_case, (uuid) in parameters.items():
            print(f"... testcase: {test_case}")
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup(change_log_file_name=change_log_file)
            result = self.mm.delete_change_log_element(uuid)
            assert(result==assertions[test_case])
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

class Test_MetadataManager_get_change_log(unittest.TestCase):

    def setUp(self):
        pass

    def test_MetadataManager_get_change_log(self):
        print("TESTING: test_MetadataManager_update_change_log")
        self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
        

        parameters = {
            "valid": "change_log.json"
        }

        assertions = {
           "valid": ("c86a53a6-8ccc-11f0-a3aa-325096b39f47",2)
        }

        self.tearDown()

        for test_case, (file_name) in parameters.items():
            print(f"... testcase: {test_case}")
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup(change_log_file_name=file_name)
            result = self.mm.get_change_log()
            assert(len(result[assertions[test_case][0]])==assertions[test_case][1])
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

#Source: https://stackoverflow.com/questions/5360833/how-do-i-run-multiple-classes-in-a-single-test-suite-in-python-using-unit-testin
def run_tests():
    MetadataManager_test_cases = [# Test_MetadataManager_value_conflict_exists,          #done
                                  # Test_MetadataManager_get_max_write_prio_element,     #done
                                  # Test_MetadataManager_get_model_element,              #done 
                                  # Test_MetadataManager_get_mapped_domain_elements,     #done
                                  # Test_MetadataManager_remove_mapping,                #done
                                  # Test_MetadataManager_get_Mappings_elements,          #done 
                                  # Test_MetadataManager_apply_value_changes_to_mapping, #done ln 516 in metadata_manager must be commented out for test to run since no Strvar is initialized
                                  #Test_MetadataManager_update_sysml_model,           #done
                                  #Test_MetadataManager_manager_consistency            #done
                                  Test_MetadataManager_get_change_log,
                                  Test_MetadataManager_update_change_log,
                                  Test_MetadataManager_delete_change_log_element
                                ]
    loader = unittest.TestLoader()

    suites_list = []

    for test_class in MetadataManager_test_cases:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    AUTOSAR_Parser_test_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(AUTOSAR_Parser_test_suite)

if __name__ == '__main__':
    result = run_tests()