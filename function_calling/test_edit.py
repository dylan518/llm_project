import unittest
import os
from code_parser_replace import CodeModifier, CodeModification, ModificationGenerator

# Assuming CodeModifier and CodeModification are defined as above

class TestCodeModifier(unittest.TestCase):

    def setUp(self):
        # Set up a temporary file for testing
        self.test_file_path = "test_file.py"
        with open(self.test_file_path, "w") as file:
            file.write("print('Hello, world!')\n")

    def tearDown(self):
        # Clean up after tests
        os.remove(self.test_file_path)

    def test_apply_modifications(self):
        modifier = CodeModifier(self.test_file_path)
        modifications = [
            {'line_number': [1, 1], 'code': "print('Goodbye, world!')"}
        ]
        modifier.apply_modifications(modifications)
        with open(self.test_file_path, "r") as file:
            content = file.read()
        self.assertIn("Goodbye, world!", content)

    def test_check_code_compiles(self):
        modifier = CodeModifier(self.test_file_path)
        modifications = [
            {'line_number': [1, 1], 'code': "print('Goodbye, world!')"}
        ]
        self.assertTrue(modifier.check_code_compiles(modifications))

class TestCodeModification(unittest.TestCase):

    def test_validate_modifications(self):
        valid_modifications = {
            "modifications": [
                {"line_number": [1, 1], "code": "print('Test')"}
            ]
        }
        try:
            code_modification = CodeModification(file_path="test_file.py", **valid_modifications)
        except Exception as e:
            self.fail(f"CodeModification validation failed with exception: {e}")

    def test_invalid_modifications(self):
        invalid_modifications = {
            "modifications": [
                {"line_number": [1, 1]}  # Missing 'code' key
            ]
        }
        with self.assertRaises(ValueError):
            CodeModification(file_path="test_file.py", **invalid_modifications)

class TestModificationGenerator(unittest.TestCase):

    def setUp(self):
        # Create a test file
        self.test_file_path = "example_script.py"
        with open(self.test_file_path, "w") as file:
            file.write("def greet(name):\n    print(f'Hello, {name}')\n\ngreet('World')\n")

        # Initialize ModificationGenerator with the test file path
        self.mod_generator = ModificationGenerator(filepath=self.test_file_path, openai_key="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")

    def tearDown(self):
        # Clean up after test
        os.remove(self.test_file_path)

    def test_generate_modifications(self):
        # Example messages and code changes
        messages = ["Change the greeting message to 'Welcome'"]
        code = "def greet(name):\n    print(f'Hello, {name}')\n\ngreet('World')\n"

        # Generate modifications
        modifications = self.mod_generator.generate_modifications(messages, code)

        # Apply modifications if any
        if modifications and modifications.modifications:
            self.mod_generator.modifier.apply_modifications([mod.dict() for mod in modifications.modifications])

            # Check if the modifications were applied
            with open(self.test_file_path, "r") as file:
                content = file.read()
            self.assertIn("Welcome", content)

    def setUp(self):
        # Create a test file with the original script
        self.test_file_path = "example_script.py"
        with open(self.test_file_path, "w") as file:
            file.write(
                "def factorial(n):\n"
                "    if n == 1:\n"
                "        return 1\n"
                "    else:\n"
                "        return n * factorial(n - 1)\n\n"
                "print(factorial(5))\n"
            )

        self.mod_generator = ModificationGenerator(filepath=self.test_file_path, openai_key="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")

    def tearDown(self):
        os.remove(self.test_file_path)

    def test_complex_modifications(self):
        messages = ["Refactor the factorial function to use iteration instead of recursion, "
                    "add error handling for negative inputs, "
                    "and add a new function to calculate the sum of all numbers up to the given number."]

        code = (
            "def factorial(n):\n"
            "    if n == 1:\n"
            "        return 1\n"
            "    else:\n"
            "        return n * factorial(n - 1)\n\n"
            "print(factorial(5))\n"
        )

        # Generate modifications
        modifications = self.mod_generator.generate_modifications(messages, code)

        # Apply modifications if any
        if modifications and modifications.modifications:
            self.mod_generator.modifier.apply_modifications([mod.dict() for mod in modifications.modifications])

            # Read and print the modified file
            with open(self.test_file_path, "r") as file:
                modified_content = file.read()
                print("Modified Content:\n", modified_content)

# Run the tests
if __name__ == '__main__':
    unittest.main()
