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

class Test_SysmlParser_get_value(unittest.TestCase):

    """
    Testcases:
        invalid elementPath(None, "", invalid, leading to no attribute value)
        valid
    """
    def setUp(self):
        pass

    def test_SysmlParser_get_value(self):
        print(f"TESTING: test_SysmlParser_get_value")
        
        parameters = {
            "invalid_content_not_loaded": "sysml_elements.sysml_elem_o2o_nvc.sysml_attrib_3",
            "invalid_elementPath_is_None": None,
            "invalid_elementPath_is_empty_str": "",
            "invalid_elementPath_does_not_exist_1": "invalid_path_123",
            "invalid_elementPath_does_not_exist_2": "sysml_elements.sysml_elem_o2o_nvc.sysml_attrib_3.invalid",
            "invalid_elementPath_target_has_no_value": "sysml_elements.sysml_elem_m2o_vc",
            "valid": "sysml_elements.sysml_elem_o2o_nvc.sysml_attrib_3"
        }

        assertions = {
            "invalid_content_not_loaded": None,
            "invalid_elementPath_is_None": None,
            "invalid_elementPath_is_empty_str":None,
            "invalid_elementPath_does_not_exist_1":None,
            "invalid_elementPath_does_not_exist_2": None,
            "invalid_elementPath_target_has_no_value":None,
            "valid":"Component_1"
        }

        for test_case, elementPath in parameters.items():
            print(f"test_case: {test_case}")
            self.fp_AUTOSAR, self.fp_code, self.fp_gerber, self.fp_step, self.fp_sysml, self.mm, self.app, self.vc, self.files = global_setup()
            if test_case == "invalid_content_not_loaded": self.fp_sysml.sysml_path=None
            result = self.fp_sysml.get_value(elementPath=elementPath)
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

def global_setup(sysml_file_name=None,gerber_file_name=None,AUTOSAR_file_name=None, code_file_name=None, step_file_Name=None, testing_file_path=None, backup_file_path=None, mapping_file_name=None,change_log_file_name=None ):
    
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
    GUI_test_cases = [
                        Test_SysmlParser_get_value
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