import unittest
from code_parser import CodeModifier, CodeModification  # Replace with actual import
import tempfile
import os
import json


class TestCodeModification(unittest.TestCase):

    def test_get_format_instructions(self):
        expected = {
            "description":
            "Provide code modification details in JSON format.",
            "format":
            '{"modifications": [{"action": "add"|"delete", "line_number": int | [start, end], "code": "string"}, ...]}'
        }
        result = CodeModification.get_format_instructions()
        self.assertEqual(result, expected)


class TestCodeModifier(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_file_path = os.path.join(self.temp_dir.name, "temp_file.py")
        with open(self.temp_file_path, 'w') as file:
            file.write("print('hello world')\n")
        self.code_modifier = CodeModifier(self.temp_file_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_construct_query(self):
        messages = ["modify code"]
        code = "print('goodbye world')\n"
        expected = "Message: modify code\nCode:\n1: print('goodbye world')\n"
        result = self.code_modifier.construct_query(messages, code)
        self.assertEqual(result, expected)

    def test_generate_modifications(self):
        # Mock the GPT-4 model to return a predefined output
        self.code_modifier.model = MagicMock()
        self.code_modifier.model.return_value = {
            "modifications": [{
                "action": "add",
                "line_number": 2,
                "code": "print('goodbye world')"
            }]
        }
        messages = ["add print statement"]
        code = "print('hello world')\n"
        expected_modifications = CodeModification(
            action=["add"], line_number=[2], code=["print('goodbye world')"])
        result_modifications = self.code_modifier.generate_modifications(
            messages, code)
        self.assertEqual(result_modifications, expected_modifications)

    def test_check_code_compiles(self):
        modification = CodeModification(action=["add"],
                                        line_number=[2],
                                        code=["print('code compiles')"])
        result = self.code_modifier.check_code_compiles(modification)
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
