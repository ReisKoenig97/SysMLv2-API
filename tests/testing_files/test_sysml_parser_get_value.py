import unittest
from file_parser import SysmlParser

class Test_SysmlParser_get_value(unittest.TestCase):
    """
    Test Cases:
        None as elementPath
        "" as elementPath
        randomn String als ElementPath
        elementPath that leads to nowhere
        valid elementPath
    """
    def setUp(self):
        self.fp_sysml = SysmlParser(sysml_path="./sysml_file.sysml")
    
    def tearDown(self):
        self.fp_sysml = None
    
    def Test_SysmlParser_get_value_None_as_elementPath(self):
        result = self.fp_sysml.get_value(None)
        assert(result == None)
    
    def Test_SysmlParser_get_value_empty_str_as_elementPath(self):
        result = self.fp_sysml.get_value("")
        assert(result == None)
    
    def Test_SysmlParser_get_value_randomn_str_as_elementPath(self):
        result = self.fp_sysml.get_value("this is not a path")
        assert(result == None)
    
    def Test_SysmlParser_get_value_invalid_path_as_elementPath_1(self):
        result = self.fp_sysml.get_value("sysml_elements.sysml_elem_m2o_vc.no_attribute")
        assert(result == None)

    def Test_SysmlParser_get_value_invalid_path_as_elementPath_2(self):
        result = self.fp_sysml.get_value("sysml_elements.no_part_def.no_attribute")
        assert(result == None)

    def Test_SysmlParser_get_value_invalid_path_as_elementPath_3(self):
        result = self.fp_sysml.get_value("no_sysml_elements.sysml_elem_m2o_vc.no_attribute")
        assert(result == None)
    
    def Test_SysmlParser_get_value_valid_path_as_elementPath_1(self):
        result = self.fp_sysml.get_value("sysml_elements.sysml_elem_m2o_vc.sysml_attrib_2")
        assert(result == "Path/To/Whereever")


#Source: https://stackoverflow.com/questions/5360833/how-do-i-run-multiple-classes-in-a-single-test-suite-in-python-using-unit-testin
def run_tests():
    MetadataManager_test_cases = [Test_SysmlParser_get_value]
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