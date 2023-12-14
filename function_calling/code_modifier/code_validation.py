import os
import shutil
import py_compile
import tempfile
from typing import List
from pydantic import BaseModel, Field, validator, ValidationError
from code_modifier import CodeModifier

class CodeModifier:

    def __init__(self, filepath):
        self.filepath = filepath

    def apply_modifications(self, modifications):
        with open(self.filepath, 'r') as file:
            lines = file.readlines()

        for mod in modifications:
            line_range, new_code = mod['line_number'], mod['code']
            start_line, end_line = [x - 1 for x in line_range]  # Adjusting line numbers to 0-based indexing

            # Ensure the new code ends with a newline character
            if not new_code.endswith('\n'):
                new_code += '\n'

            # Replace the specified range of lines with the new code
            lines[start_line:end_line + 1] = new_code.splitlines(keepends=True)

        # Write the modified code back to the file
        with open(self.filepath, 'w') as file:
            file.writelines(lines)

    def check_code_compiles(self, modifications):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file_path = os.path.join(temp_dir, "temp_file.py")
            shutil.copyfile(self.filepath, temp_file_path)
            # Create a new CodeModifier instance for the temporary file
            temp_modifier = CodeModifier(temp_file_path)
            print(f"Applied modifications\n{modifications}")
            temp_modifier.apply_modifications(modifications)
            try:
                py_compile.compile(temp_file_path, doraise=True)
                return True
            except py_compile.PyCompileError as e:
                print(f"Compilation error: {e}")
                return False

class CodeModification(BaseModel):

    class Modification(BaseModel):
        line_number: List[int] = Field(..., description="A list containing the start and end line numbers for the replacement range.")
        code: str = Field(..., description="The new code that will replace the code in the specified line range.")

        @validator('line_number')
        def validate_line_number(cls, v):
            if not isinstance(v, list) or len(v) != 2 or not all(isinstance(n, int) for n in v):
                raise ValueError("line_number must be a list of two integers")
            if v[0] > v[1]:
                raise ValueError("Start line must be less than or equal to end line")
            return v

        @validator('code')
        def validate_code(cls, v):
            if not v.strip():
                raise ValueError("code must be a non-empty string")
            return v
    
    modifications: List[Modification] = Field(..., description="List of code modifications.")

    class Config:
        arbitrary_types_allowed = True

    def initialize_modifier(self, file_path: str):
            self._modifier = CodeModifier(file_path)
    
    @validator("modifications", pre=True)
    def validator(cls, modifications, values, **kwargs):
        if not isinstance(modifications, list):
            raise ValueError("modifications should be a list of modification objects")

        mod_instances = []
        for modification_dict in modifications:
            # Check if 'code' key exists and is not empty
            if 'code' not in modification_dict or not modification_dict['code'].strip():
                raise ValueError("Each modification must include a non-empty 'code' string")

            # Replace escaped newline and tab characters
            modification_dict['code'] = modification_dict['code'].replace('\\n', '\n').replace('\\t', '\t')

            try:
                # Create Modification instance and add to the list
                mod_instance = cls.Modification(**modification_dict)
                mod_instances.append(mod_instance)
            except ValidationError as e:
                raise ValueError(f"Invalid modification format: {e}")

        # Assuming modifier initialization is handled elsewhere, such as in a post-init method
        if hasattr(cls, '_modifier') and not cls._modifier.check_code_compiles(mod_instances):
            raise ValueError("Modification causes compile failure")

        return modifications

    @staticmethod
    def get_format_instructions():
        return {
            "description": "Provide code modification details in JSON format for code replacements.",
            "format": '{"modifications": [{"line_number": [start_line, end_line], "code": "replacement code string"}, ...]}'
        }