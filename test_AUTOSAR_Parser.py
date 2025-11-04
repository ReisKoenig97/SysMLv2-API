import unittest
from AUTOSAR_Parser import AUTOSAR_Parser
from utils.json_utils import save_json, load_json

class Test_AUTOSAR_Parser_load_file(unittest.TestCase):
    """
    testcases:
        None as file_path
        "" as file path
        string as file_path that is not in file path syntax
        invalid file path
        filepath to file without xml syntax
        valid file path to valid file
    """
    def setUp(self):
        self.fp_AUTOSAR = AUTOSAR_Parser(AUTOSAR_file_path=None)
    def tearDown(self):
        self.fp_AUTOSAR = None

    def test_AUTOSAR_Parser_load_file_None_as_file_Path(self):
        assert(self.fp_AUTOSAR.load_file(None) == None)

    def test_AUTOSAR_Parser_load_file_empty_str_file_Path(self):
        assert(self.fp_AUTOSAR.load_file("") == None)
    
    def test_AUTOSAR_Parser_load_file_invalid_str(self):
        assert(self.fp_AUTOSAR.load_file("ringsinare") == None)

    def test_AUTOSAR_Parser_load_nonexistent_file_path(self):
        assert(self.fp_AUTOSAR.load_file("/xyz/abc/def.arxml") == None)

    def test_AUTOSAR_Parser_load_file_path_to_non_arxml(self):
        self.assertRaises(Exception, self.fp_AUTOSAR.load_file("./tests/testing_files/normal_text_file.txt"))

    def test_AUTOSAR_Parser_load_file_valid(self):
        file_content_tree = self.fp_AUTOSAR.load_file("./tests/testing_files/arxml_domain.arxml")
        assert(self.fp_AUTOSAR.tree_root.tag.split("}")[-1] == "AUTOSAR" and file_content_tree.getroot().tag.split("}")[-1] == "AUTOSAR")
    
class Test_AUTOSAR_Parser_get_value(unittest.TestCase):
    """
    testcases:
        None as elementPath
        "" as elementPath
        nonexistent elementPath with fitting Syntax
        valid elementPath with and without adressing of tags
        path to element without text value
    """
    def setUp(self):
        self.fp_AUTOSAR = AUTOSAR_Parser("./tests/testing_files/arxml_domain.arxml")
    def tearDown(self):
        self.fp_AUTOSAR = None

    def test_AUTOSAR_Parser_get_value_None_as_elementPath(self):
        element_value = self.fp_AUTOSAR.get_value(None)
        assert(element_value == None)

    def test_AUTOSAR_Parser_get_value_empty_str_as_elementPath(self):
        element_value = self.fp_AUTOSAR.get_value("")
        assert(element_value == None)

    def test_AUTOSAR_Parser_get_value_nonexistent_elementPath_1(self):
        element_value = self.fp_AUTOSAR.get_value("Components.INVALID.MOREINVALID.Component_1")
        assert(element_value == None)

    def test_AUTOSAR_Parser_get_value_nonexistent_elementPath_2(self):
        element_value = self.fp_AUTOSAR.get_value("INVALID.MOREINVALID.Component_1")
        assert(element_value == None)

    def test_AUTOSAR_Parser_get_value_randomn_str_as_elementPath(self):
        element_value = self.fp_AUTOSAR.get_value("randomnString is the elementPath here")
        assert(element_value == None)

    def test_AUTOSAR_Parser_get_value_valid_elementPath_1(self):
        element_value = self.fp_AUTOSAR.get_value("ComponentTypes.Component_1.SHORT-NAME")
        assert(element_value == "Component_1")

    def test_AUTOSAR_Parser_get_value_valid_elementPath_2(self):
        element_value = self.fp_AUTOSAR.get_value("ComponentTypes.Component_1.PORTS.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC.DATA-ELEMENT-REF")
        assert(element_value == "/PortInterfaces/Comp_1_to_Comp_2/Comp_1_value_1")

    def test_AUTOSAR_Parser_get_value_valid_elementPath_3(self):
        element_value = self.fp_AUTOSAR.get_value("ComponentTypes.Component_1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC.DATA-ELEMENT-REF")
        assert(element_value == "/PortInterfaces/Comp_1_to_Comp_2/Comp_1_value_1")

    def test_AUTOSAR_Parser_get_value_invalid_elementPath_1(self):
        element_value = self.fp_AUTOSAR.get_value("ComponentTypes.Component_1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC")
        assert(element_value == None)

class Test_AUTOSAR_Parser_find_elem(unittest.TestCase):
    """
    testcases:
        None as elementPath
        "" as elementPath
        nonexistent elementPath with fitting Syntax
        elementPath with wrong Syntax
        path that does not end with xml tag
        valid elementPath without Adressing of tags
        valid ElementPath with adressin of tags
    """
    def setUp(self):
        self.fp_AUTOSAR = AUTOSAR_Parser("./tests/testing_files/arxml_domain.arxml")
    def tearDown(self):
        self.fp_AUTOSAR = None

    def test_AUTOSAR_Parser_find_elem_None_as_elementPath(self):
        element = self.fp_AUTOSAR.find_elem(None)
        assert(element == None)

    def test_AUTOSAR_Parser_find_elem_empty_str_as_elementPath(self):
        element = self.fp_AUTOSAR.find_elem("")
        assert(element == None)

    def test_AUTOSAR_Parser_find_elem_nonexistent_elementPath_1(self):
        element = self.fp_AUTOSAR.find_elem("Components.INVALID.MOREINVALID.Component_1",reload_file=True)
        assert(element == None)

    def test_AUTOSAR_Parser_find_elem_nonexistent_elementPath_2(self):
        element = self.fp_AUTOSAR.find_elem("INVALID.MOREINVALID.Component_1")
        assert(element == None)

    def test_AUTOSAR_Parser_find_elem_randomn_str_as_elementPath(self):
        element = self.fp_AUTOSAR.find_elem("randomnString is the elementPath here")
        assert(element == None)

    def test_AUTOSAR_Parser_find_elem_valid_elementPath_1(self):
        element = self.fp_AUTOSAR.find_elem("ComponentTypes.Component_1.SHORT-NAME")
        assert(element.text == "Component_1")

    def test_AUTOSAR_Parser_find_elem_valid_elementPath_2(self):
        element = self.fp_AUTOSAR.find_elem("ComponentTypes.Component_1.PORTS.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC.DATA-ELEMENT-REF")
        assert(element.text == "/PortInterfaces/Comp_1_to_Comp_2/Comp_1_value_1")

    def test_AUTOSAR_Parser_find_elem_valid_elementPath_3(self):
        element = self.fp_AUTOSAR.find_elem("ComponentTypes.Component_1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC.DATA-ELEMENT-REF")
        assert(element.text == "/PortInterfaces/Comp_1_to_Comp_2/Comp_1_value_1")

    def test_AUTOSAR_Parser_find_elem_valid_elementPath_4(self):
        element = self.fp_AUTOSAR.find_elem("ComponentTypes.Component_1.snd_Value_1")
        assert(element.tag.split("}")[-1] == "P-PORT-PROTOTYPE")
    
class Test_AUTOSAR_Parser_set_value(unittest.TestCase):
    """
    testcases:
        path to element without text value
        None as Value
        "" as Value
        valid path
        setting of reference(invalid and valid)
        setting of SHORT-NAME(invalid and valid)
    """
    
    def setUp(self):
        self.fp_AUTOSAR = AUTOSAR_Parser("./tests/testing_files/arxml_domain.arxml")
        self.mapping = load_json("./tests/testing_files/empty_json.json")
    def tearDown(self):
        try:
            with open("./tests/testing_files/backup/arxml_domain.arxml", "r") as src, open("./tests/testing_files/arxml_domain.arxml", "w") as dest:
                dest.write(src.read())
        except Exception:
            print("error restoring arxml_domain.arxml")
        self.fp_AUTOSAR = None

    def test_AUTOSAR_Parser_set_value_path_to_element_without_text_value(self):
        print("Testing test_AUTOSAR_Parser_set_value_path_to_element_without_text_value")
        set_was_successful = self.fp_AUTOSAR.set_value("ComponentTypes.Component_1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC", "Hello",self.mapping)
        assert(set_was_successful == False)
    
    def test_AUTOSAR_Parser_set_value_none_as_value(self):
        print("Testing: test_AUTOSAR_Parser_set_value_none_as_value")
        set_was_successful = self.fp_AUTOSAR.set_value("ComponentTypes.Component_1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC.INIT-VALUE.NUMERICAL-VALUE-SPECIFICATION.VALUE", None,self.mapping)
        assert(set_was_successful == False)
    
    def test_AUTOSAR_Parser_set_value_empty_str_as_value(self):
        print("Testing: test_AUTOSAR_Parser_set_value_empty_str_as_value")
        set_was_successful = self.fp_AUTOSAR.set_value("ComponentTypes.Component_1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC.INIT-VALUE.NUMERICAL-VALUE-SPECIFICATION.VALUE", "",self.mapping)
        assert(set_was_successful == False)

    def test_AUTOSAR_Parser_set_value_invalid_ref_1(self):
        print("Testing: test_AUTOSAR_Parser_set_value_invalid_ref_1")
        set_was_successful = self.fp_AUTOSAR.set_value("ComponentTypes.Component_1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC.DATA-ELEMENT-REF", "Hello",self.mapping)
        assert(set_was_successful == False)

    def test_AUTOSAR_Parser_set_value_invalid_ref_2(self):
        print("Testing: test_AUTOSAR_Parser_set_value_invalid_ref_2")
        set_was_successful = self.fp_AUTOSAR.set_value("ComponentTypes.Component_1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC.DATA-ELEMENT-REF", "/ComponentTypes/Componet_1/snd_Value_1",self.mapping)
        assert(set_was_successful == False)

    def test_AUTOSAR_Parser_set_value_invalid_short_name(self):
        print("Testing: test_AUTOSAR_Parser_set_value_invalid_short_name")
        set_was_successful = self.fp_AUTOSAR.set_value("ComponentTypes.Component_1.SHORT-NAME", "Component_2",self.mapping)
        assert(set_was_successful == False)

    def test_AUTOSAR_Parser_set_value_invalid_mapping(self):
        print("Testing: test_AUTOSAR_Parser_set_value_invalid_mapping")
        set_was_successful = self.fp_AUTOSAR.set_value("ComponentTypes.Component_1.SHORT-NAME", "Component_2",None)
        assert(set_was_successful == False)


    def test_AUTOSAR_Parser_set_value_valid_ref(self):
        print("Testing: test_AUTOSAR_Parser_set_value_valid_ref")
        set_was_successful = self.fp_AUTOSAR.set_value("ComponentTypes.Component_1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC.DATA-ELEMENT-REF", "/ComponentTypes/Component_1/Component_1_InternalBehavior/InterRunnableVariable_Value_1",self.mapping)
        assert(set_was_successful == True)
        assert(self.fp_AUTOSAR.get_value("ComponentTypes.Component_1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC.DATA-ELEMENT-REF") == "/ComponentTypes/Component_1/Component_1_InternalBehavior/InterRunnableVariable_Value_1")

    def test_AUTOSAR_Parser_set_value_set_short_name(self):
        print("Testing: test_AUTOSAR_Parser_set_value_set_short_name")
        set_was_successful = self.fp_AUTOSAR.set_value("ComponentTypes.Component_1.snd_Value_1.SHORT-NAME","new_short_name_for_sndvalue1",self.mapping)
        assert(set_was_successful == True)
        assert(self.fp_AUTOSAR.get_value("ComponentTypes.Component_1.new_short_name_for_sndvalue1.SHORT-NAME",reload_file=True) == "new_short_name_for_sndvalue1")
        assert(self.fp_AUTOSAR.get_value("ComponentTypes.ECU_1.Component_1_snd_Value_1_Component_2_rcv_Value_1.PROVIDER-IREF.TARGET-P-PORT-REF",reload_file=True) == "/ComponentTypes/Component_1/new_short_name_for_sndvalue1")
        assert(self.fp_AUTOSAR.get_value("ComponentTypes.Component_1.Component_1_InternalBehavior.Runnable_20ms.SEND_snd_Value_1_Comp_1_value_1.ACCESSED-VARIABLE.AUTOSAR-VARIABLE-IREF.PORT-PROTOTYPE-REF", reload_file=True) == "/ComponentTypes/Component_1/new_short_name_for_sndvalue1")

    def test_AUTOSAR_Parser_set_value_valid_elem(self):
        print("Testing: test_AUTOSAR_Parser_set_value_valid_elem")
        set_was_successful = self.fp_AUTOSAR.set_value("ComponentTypes.Component_1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC.INIT-VALUE.NUMERICAL-VALUE-SPECIFICATION.VALUE", "30",self.mapping)
        assert(set_was_successful == True)
        assert(self.fp_AUTOSAR.get_value("ComponentTypes.Component_1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC.INIT-VALUE.NUMERICAL-VALUE-SPECIFICATION.VALUE",reload_file=True) == "30")

class Test_AUTOSAR_Parser_get_AUTOSAR_only_path(unittest.TestCase):
    """
    TestCases:
    None as Element
    Element without Short Name child
    valid Element
    """
    def setUp(self):
        self.fp_AUTOSAR = AUTOSAR_Parser("./tests/testing_files/arxml_domain.arxml")
    def tearDown(self):
        self.fp_AUTOSAR = None

    def test_AUTOSAR_Parser_get_AUTOSAR_only_path_None_as_element(self):
        path = self.fp_AUTOSAR.get_AUTOSAR_only_path(None)
        assert(path == None)

    def test_AUTOSAR_Parser_get_AUTOSAR_only_path_element_without_short_name_child(self):
        path = self.fp_AUTOSAR.get_AUTOSAR_only_path(self.fp_AUTOSAR.find_elem("ComponentTypes.Component_1.snd_Value_1.PROVIDED-COM-SPECS.NONQUEUED-SENDER-COM-SPEC"))
        assert(path == "/ComponentTypes/Component_1/snd_Value_1")

    def test_AUTOSAR_Parser_get_AUTOSAR_only_path_valid_element(self):
        path = self.fp_AUTOSAR.get_AUTOSAR_only_path(self.fp_AUTOSAR.find_elem("ComponentTypes.Component_1.snd_Value_1"))
        assert(path == "/ComponentTypes/Component_1/snd_Value_1")

#Source: https://stackoverflow.com/questions/5360833/how-do-i-run-multiple-classes-in-a-single-test-suite-in-python-using-unit-testin
def run_tests():
    AUTOSAR_Parser_test_cases = [Test_AUTOSAR_Parser_load_file,
                                 Test_AUTOSAR_Parser_get_value,
                                 Test_AUTOSAR_Parser_find_elem,
                                 Test_AUTOSAR_Parser_set_value,
                                 Test_AUTOSAR_Parser_get_AUTOSAR_only_path
                                 ]
    loader = unittest.TestLoader()

    suites_list = []

    for test_class in AUTOSAR_Parser_test_cases:
        suite = loader.loadTestsFromTestCase(test_class)
        suites_list.append(suite)

    AUTOSAR_Parser_test_suite = unittest.TestSuite(suites_list)

    runner = unittest.TextTestRunner()
    results = runner.run(AUTOSAR_Parser_test_suite)

if __name__ == '__main__':
    result = run_tests()