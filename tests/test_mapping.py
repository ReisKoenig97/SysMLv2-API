import unittest
from unittest import mock # for mocking to simulate the behavior of external dependencies and objects
import os
import tempfile
import json
from datetime import datetime
from metadata_manager import MetadataManager 
from utils.config_utils import load_config
import time


class TestMapMetadata(unittest.TestCase):

    def setUp(self):
        # temporary Mapping-File
        self.temp_mapping_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_mapping_path = self.temp_mapping_file.name
        self.temp_mapping_file.close()  # Close the file so it can be used later

        # test-class initialize with map_metadata 
        DEFAULT_CONFIG_FILE = "config/default_config.json" 
        DEFAULT_CONFIG = load_config(DEFAULT_CONFIG_FILE)

        mock_gerberparser = mock.Mock()
        mock_gerberparser.get_value.return_value = "abc" # 12.5
       

        self.tool = MetadataManager(config=DEFAULT_CONFIG, 
                                    gerberparser=mock_gerberparser)
        self.tool.mapping_file_path = self.temp_mapping_path

        # create empty mapping file 
        empty_mapping = {
            "SysMLv2": [],
            "Mappings": []
        }
        with open(self.temp_mapping_path, "w") as f:
            json.dump(empty_mapping, f)

        # test-files 
        self.sysml_path = tempfile.NamedTemporaryFile(delete=False, suffix=".sysml").name # suffix=".txt"
        self.domain_path = tempfile.NamedTemporaryFile(delete=False, suffix=".gbrjob").name
        # self.temp_sysml_path = self.sysml_file
        # self.temp_domain_path = self.domain_file
        # self.temp_sysml_path.close() 
        # self.temp_domain_path.close()

    def tearDown(self):
        os.remove(self.temp_mapping_path)
        os.remove(self.sysml_path)
        os.remove(self.domain_path)

    # Test if fields are complete 
    def test_data_completeness(self):
        sample_entry = {
            "uuid": "e8f252fb-1303-411e-8ddf-d09adfac84eb",
            "name": "Length",
            "value": "12.5", # 12.5
            "unit": "mm",
            "index": "0",
            "datatype": "",
            "element_path": "package.partA.len",
            "file_path": self.sysml_path,
            "created_at": str(datetime.now()),
            "lastModified": str(datetime.now())
        }

        required_fields = ["uuid", "name", "value", "unit", "datatype", "element_path", "file_path", "created_at", "lastModified"]
        for field in required_fields:
            self.assertIn(field, sample_entry, f"{field} is missing!")

    # Test if values are the same -> should be true (not FAILED)
    def test_mapping_basic_real_value(self):
        result = self.tool.map_metadata(
            sysml_path=self.sysml_path,
            sysml_element_path="package.partA.len",
            sysml_element_value="12.5", # CHANGE this to test different values
            sysml_element_unit="mm",
            domain_file_format="GerberJobFile",
            domain_path=self.domain_path,
            domain_element_path="GeneralSpecs.Size.X",
            domain_element_value="12.5",
            domain_element_unit="mm"
        )
        self.assertTrue(result)

    # Test if datatype of the values are the same
    def test_mapping_type_mismatch(self):
        #result = None 
        with self.assertRaises(ValueError) as context:
            self.tool.map_metadata(
                sysml_path=self.sysml_path,
                sysml_element_path="package.partA.len",
                sysml_element_value="123", # test wrong datatype as string that is checked by map_metadata function
                sysml_element_unit="mm",
                domain_file_format="GerberJobFile",
                domain_path=self.domain_path,
                domain_element_path="GeneralSpecs.Size.X",
                domain_element_value="abc",
                domain_element_unit="mm"
            )
        self.assertIn("Datatype mismatch", str(context.exception))

    # Test if units are the same
    def test_mapping_unit_mismatch(self):
        with self.assertRaises(ValueError) as context:
            self.tool.map_metadata(
                sysml_path=self.sysml_path,
                sysml_element_path="package.partA.len",
                sysml_element_value="12.5",
                sysml_element_unit="mm",
                domain_file_format="GerberJobFile",
                domain_path=self.domain_path,
                domain_element_path="GeneralSpecs.Size.X",
                domain_element_value="12.5",
                domain_element_unit="cm"
            )
        self.assertIn("Unit mismatch", str(context.exception))



    def test_scalability_with_many_mappings(self):
        # Anzahl der zu testenden Mappings (z. B. 1000 für Stresstest)
        num_mappings = 1000
        start_time = time.time()

        for i in range(num_mappings):
            sysml_element_path = f"package.partA.len{i}"
            sysml_element_value = str(10.0 + i)
            domain_element_path = f"GeneralSpecs.Size.X{i}"
            domain_element_value = str(10.0 + i)

            result = self.tool.map_metadata(
                sysml_path=self.sysml_path,
                sysml_element_path=sysml_element_path,
                sysml_element_value=sysml_element_value,
                sysml_element_unit="mm",
                domain_file_format="GerberJobFile",
                domain_path=self.domain_path,
                domain_element_path=domain_element_path,
                domain_element_value=domain_element_value,
                domain_element_unit="mm"
            )
            self.assertTrue(result, f"Mapping {i} failed")

        duration = time.time() - start_time
        print(f"Duration for {num_mappings} mappings: {duration:.2f} seconds")

        threshold = 10.0 #seconds
        if duration > threshold:
            print(f"Warning: Duration exceeded threshold of {threshold} seconds")

        # Lade Mapping-File und prüfe, ob alle Einträge vorhanden sind
        with open(self.tool.mapping_file_path, "r") as f:
            data = json.load(f)

        self.assertEqual(len(data["SysMLv2"]), num_mappings)
        self.assertEqual(len(data["GerberJobFile"]), num_mappings)
        self.assertEqual(len(data["Mappings"]), num_mappings)


    def test_error_detection_rate2(self):
        num_errors = 10
        detected_errors = 0

        for i in range(num_errors):
            # Standardwerte für den Normalfall
            sysml_value = "10.0"
            domain_value = "10.0"
            unit1 = "mm"
            unit2 = "mm"

            sysml_element_path = f"package.partB.len{i}"
            domain_element_path = f"GeneralSpecs.Size.X{i}"

            # Fehlerart 1: unterschiedliche Einheiten
            if i % 2 == 0:
                unit2 = "inch"

            # Fehlerart 2: leere Werte
            if i % 2 == 1:
                sysml_value = ""
                domain_value = ""

            try:
                result = self.tool.map_metadata(
                    sysml_path=self.sysml_path,
                    sysml_element_path=sysml_element_path,
                    sysml_element_value=sysml_value,
                    sysml_element_unit=unit1,
                    domain_file_format="GerberJobFile",
                    domain_path=self.domain_path,
                    domain_element_path=domain_element_path,
                    domain_element_value=domain_value,
                    domain_element_unit=unit2
                )

                if result is False:
                    detected_errors += 1

            except Exception:
                detected_errors += 1

        error_detection_rate = (detected_errors / num_errors) * 100
        print(f"\nError detection rate: {error_detection_rate:.2f}% ({detected_errors} of {num_errors} detected)")

        self.assertGreaterEqual(error_detection_rate, 90.0, "error detection rate is below 90%")