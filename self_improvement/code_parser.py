import tempfile
import os
from pydantic import BaseModel, Field, validator
import shutil
import py_compile
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import StringPromptTemplate
from langchain.llms import OpenAI
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
import json
import logging
from typing import List


class CodeModification(BaseModel):
    action: List[str] = Field(description="Actions to perform: add or delete")
    line_number: List[int] = Field(description="Line numbers for the actions")
    code: List[str] = Field(description="Code to add", default=[])

    @staticmethod
    def get_format_instructions():
        return {
            "description":
            "Provide code modification details in JSON format.",
            "format":
            '{"modifications": [{"action": "add"|"delete", "line_number": int | [start, end], "code": "string"}, ...]}'
        }


class CodeModifier:

    def __init__(self, filepath):
        self.examples_file = "examples.json"
        self.filepath = filepath
        self.parser = PydanticOutputParser(pydantic_object=CodeModification)
        with open(self.examples_file, 'r') as file:
            self.examples = json.load(file)
        self.example_prompt = PromptTemplate(
            input_variables=["action", "line_number", "code"],
            template="{action} at line {line_number}: {code}\n")
        self.prompt = FewShotPromptTemplate(
            examples=self.examples,
            example_prompt=self.example_prompt,
            suffix=
            ("Based on the last message, determine if code modifications are needed."
             "\nJust because code is provided doesn't mean it should be added."
             "\nDetermine if it was meant to be incorporated into the codebase and if it will actually work."
             "\nIf no modifications are desired, do not suggest any adds or deletes."
             "\n{format_instructions}\n{query}\n"),
            input_variables=["query"])
        self.model = OpenAI(model_name="gpt-4", temperature=0.0)

    def construct_query(self, messages, code):
        try:
            # Get the last message
            last_message = messages[-1] if messages else ""

            # Add line numbers to code
            numbered_code = "\n".join(
                f"{i+1}: {line}"
                for i, line in enumerate(code.split('\n'))) if code else ""

            # Construct query
            query = f"Message: {last_message}\nCode:\n{numbered_code}"
            return query

        except Exception as e:
            logging.error(f"Error constructing query: {e}")
            return None  # or raise the exception if you prefer

    def generate_modifications(self, messages, code):
        _input = self.prompt.format_prompt(
            query=self.construct_query(messages, code))
        output = self.model(_input.to_string())
        parsed_output = self.parser.parse(output)
        return (parsed_output)

    def apply_modifications(self, filepath, modification: CodeModification):
        with open(filepath, 'r') as file:
            lines = file.readlines()

        for mod in modification.modifications:
            action = mod['action']
            line_number = mod['line_number'] - 1 if isinstance(
                mod['line_number'],
                int) else [x - 1 for x in mod['line_number']]
            code = mod['code']

            if action == 'delete':
                if isinstance(line_number, list):
                    del lines[line_number[0]:line_number[1] + 1]
                else:
                    del lines[line_number]
            elif action == 'add':
                code_lines = code.split('\n')
                for index, code_line in enumerate(code_lines):
                    lines.insert(line_number + index, code_line + '\n')

        with open(filepath, 'w') as file:
            file.writelines(lines)

    def check_code_compiles(self, modification):
        # Create a temporary directory to work in
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the original file to the temporary directory
            temp_file_path = os.path.join(temp_dir, "temp_file.py")
            shutil.copyfile(self.filepath, temp_file_path)

            # Apply the modifications to the temporary file
            self.apply_modifications(temp_file_path, modification)

            try:
                # Try compiling the entire temporary file
                py_compile.compile(temp_file_path, doraise=True)
                return True
            except py_compile.PyCompileError:
                return False
