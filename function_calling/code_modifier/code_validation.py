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

class ModificationGenerator:

    def __init__(self, filepath,openai_key):
        self.filepath = filepath
        self.modifier = CodeModifier(filepath)
        self.llm_gpt3 = OpenAI(temperature=0, model_name='gpt-4-1106-preview')
        self.parser = PydanticOutputParser(pydantic_object=CodeModification)
        self.fixer = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm_gpt3)

    def construct_query(self, messages, code):
        last_message = messages[-1] if messages else ""
        numbered_code = "\n".join(f"{i+1}: {line}" for i, line in enumerate(code.split('\n'))) if code else ""
        query = textwrap.dedent(f"""
            Message: {last_message}
            Code:
            {numbered_code}

            Based on the last message, determine if code modifications are needed.
            Return the modifications in JSON format with the following structure:

            [
                {{
                    "line_number": [start_line, end_line],
                    "code": "replacement code here"
                }},
                ... more modifications
            ]

            If no modifications are needed, return an empty list for modifications.
        """)
        return query
    
    def extract_json_from_output(self, output):
        try:
            # Find JSON boundaries
            start_idx = output.index('```json') + len('```json\n')
            end_idx = output.rindex('\n```')
            json_str = output[start_idx:end_idx]

            # Convert actual newlines in the JSON string to escaped newlines
            json_str = json_str.replace('\n', '\\n').replace('\t', '\\t')

            return json_str
        except ValueError:
            print("Unable to find JSON markers in the output.")
            return output

    def generate_modifications(self, messages, code):
        query = self.construct_query(messages, code)

        prompt = PromptTemplate(
            template="Make changes to code. \n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        _input = prompt.format_prompt(query=query)
        print(_input.to_string())

        # Generate the response
        response = self.llm_gpt3.generate(prompts=[_input.to_string()])

        # Extract the output text from the response
        response = self.llm_gpt3.generate(prompts=[_input.to_string()])

        # Extract the output text from the response
        if response.generations:
            output = response.generations[0][0].text  # Accessing the first Generation object's text
        else:
            output = ""

        output = output.replace('\\n', '\n').replace('\\t', '\t')  # Fix escaped characters
        output=self.extract_json_from_output(output)
        print(output)


        try:
            parsed_output = self.parser.parse(output)
            return parsed_output
        except ValueError as e:
            print(f"Failed to parse output: {e}")
            try:
                fixed_output = self.fixer.parse(output)
                return self.parser.parse(fixed_output)
            except Exception as ex:
                print(f"Failed to fix and parse output: {ex}")
        return None

