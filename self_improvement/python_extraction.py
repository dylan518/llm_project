import os
import shutil
import py_compile
import tempfile
from typing import List
from pydantic import BaseModel, Field, validator, ValidationError
from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import textwrap
import json

class CodeModifier:

    def __init__(self, filepath="test_file.py"):
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

    def check_code_compiles(self):
            try:
                py_compile.compile(self.filepath, doraise=True)
                return True
            except py_compile.PyCompileError as e:
                raise 



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

    modifications: List[dict] = Field(..., description="List of code modifications.")

    def __init__(self,  **data):
        # Unpack the modifications from data to create Modification instances
        super().__init__(**data) 
        mod_dicts = data.get('modifications', [])
        self.modifications = [self.Modification(**mod) for mod in mod_dicts]
        self.check_compilation()

    def check_compilation(self):
        compiler = CodeModifier()  # Use a local variable for the compiler
        for mod in self.modifications:
            compiler.apply_modifications([mod.dict()])  # Convert each Modification instance to a dict
            compiler.check_code_compiles()


    class Config:
        arbitrary_types_allowed = True

    @staticmethod
    def get_format_instructions():
        return {
            "description": "Provide code modification details in JSON format for code replacements.",
            "format": '{"modifications": [{"line_number": [start_line, end_line], "code": "replacement code string"}, ...]}'
        }



class ModificationGenerator:

    def __init__(self, filepath):
        self.filepath = filepath
        self.test_file_path = "test_file.py"
        self.modifier = CodeModifier(filepath)
        os.environ[
            "OPENAI_API_KEY"] = "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"
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
                    \n "line_number":\n [start_line, end_line],
                    "code": "replacement code here"
                }},
                ... more modifications
            ]

            If no modifications are needed, return an empty list for modifications.
        """)
        return query
    
        
    def write_to_file(self,code,file_path="test_file.py"):
        # Create a test file with the read content or empty content
        try:
            with open(file_path, 'w') as file:
                file.write(code)
        except Exception as e:
            print(f"Error writing to file {file_path}: {e}. Using empty content.")
            code_content = ""
    
    def read_from_file(self,file_path):
        try:
            with open(file_path, 'r') as file:
                code_content = file.read()
            return code_content
        except Exception as e:
            print(f"Error reading file {file_path}: {e}. Using empty content.")
            return ""

    def generate_modifications(self, messages):
        # Construct the query
        code=self.read_from_file(self.filepath) 
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
        if response.generations:
            output = response.generations[0][0].text  # Accessing the first Generation object's text
        else:
            output = ""
        
        self.write_to_file(code)
        
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

