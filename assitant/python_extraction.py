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
from llm_request import LLMRequester

class CodeModifier:

    def __init__(self, filepath="TempAX3_test_file.py"):
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

        @validator('code')
        def validate_code(cls, v):
            if not v.strip():
                raise ValueError("code must be a non-empty string")
            return v

    modifications: List[dict] = Field(..., description="List of code modifications.")

    def __init__(self,  **data):
        # Unpack the modifications from data to create Modification instances
        super().__init__(**data) 
        print(f"Data: {data}")
        mod_dicts = data.get('modifications')
        self.modifications = mod_dicts
        print(f"Modifications: {self.modifications}")
        self.check_compilation()

    def check_compilation(self):
        compiler = CodeModifier()  # Use a local variable for the compiler
        for mod in self.modifications:
            compiler.apply_modifications([mod])  # Convert each Modification instance to a dict
            compiler.check_code_compiles()
    
    def make_modifications(self):
        compiler = CodeModifier()  # Use a local variable for the compiler
        for mod in self.modifications:
            compiler.apply_modifications([mod])  # Convert each Modification instance to a dict
        return compiler.check_code_compiles()



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
        self.llm_gpt3 = OpenAI()
        self.parser = PydanticOutputParser(pydantic_object=CodeModification)
        self.fixer = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm_gpt3)

    def construct_query(self, code,proposed_changes):
        numbered_code = "\n".join(f"{i+1}: {line}" for i, line in enumerate(code.split('\n'))) if code else ""
        modifications_string='''
{
    "modifications": [
        {
            "line_number": [start_line, end_line], 
            "code": "replacement code string"
        }, ...
    ]
}'''
        query = textwrap.dedent(f'''
TASK Apply these changes to the code file, so that the new code :
Actual Code File:
```python
{numbered_code}
```
Desired Changes:
{proposed_changes}


Return the modifications in JSON format with the following structure:

{modifications_string}
            
        ''')
        return query
    
        
    def write_to_file(self,code,file_path="TempAX3_test_file.py"):
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

    def generate_modifications(self, proposed_changes):
        # Construct the query
        code=self.read_from_file(self.filepath) 
        query = self.construct_query( code, proposed_changes)

        prompt = PromptTemplate(
            template="Make changes to the code based off the proposed changes.\n{query}\n{format_instructions}",
            input_variables=["query"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        _input = prompt.format_prompt(query=query)
        print(_input.to_string())

        # Generate the response
        response = self.llm_gpt3.generate(prompts=[_input.to_string()],max_tokens=3000)
        # Extract the output text from the response
        if response.generations:
            output = response.generations[0][0].text  # Accessing the first Generation object's text
            print(response.generations[0][0].text)
        else:
            raise Exception("No response from GPT-4")
        
        self.write_to_file(code)
        
        try:
            parsed_output = self.parser.parse(output)
            return parsed_output
        except ValueError as e:
            print(f"Failed to parse output: {e}")
            try:
                fixed_output = self.fixer.parse(output)
                return fixed_output
            except Exception as ex:
                print(f"Failed to fix and parse output: {ex}")
        return None  

class make_change_to_python_file:
    def __init__(self, filepath):
        self.filepath = filepath
        self.ensure_file_prepared()
        self.modifications = ModificationGenerator(filepath)
        self.modifier = CodeModifier(filepath)
        self.requester = LLMRequester()
    
    def ensure_file_prepared(self):
        # Check if file exists
        if not os.path.exists(self.filepath):
            # Create the file with the comment '#code file is empty'
            with open(self.filepath, 'w') as file:
                file.write('#code file is empty\n')
            print(f"File '{self.filepath}' created.")
        else:
            print(f"File '{self.filepath}' already exists.")
            # Check if the file is empty
            if os.path.getsize(self.filepath) == 0:
                with open(self.filepath, 'w') as file:
                    file.write('#code file is empty\n')
                print(f"Added '#code file is empty' to the empty file '{self.filepath}'.")


    
    def read_code_from_file(self):
        try:
            with open(self.filepath, 'r') as file:
                code_content = file.read()
            return code_content
        except Exception as e:
            raise Exception(f"Error reading file {self.filepath}: {e}. Using empty content.")

    def propose_changes(self,instruction):

        os.environ[
            "OPENAI_API_KEY"] = "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"
        self.llm_gpt4 = OpenAI( )
        prompt = PromptTemplate(
            template="Write new code based off these changes in ```Python ``` markdown format. Also explain where you want it placed in the code. Try to write as much of the new code as possible. INSTRUCTIONS:{query}.\n CODE\nOLD CODE\n```python\n {code}\n ```\n\n. Write the new code",
            input_variables=["query","code"],
        )
        _input = prompt.format_prompt(query=instruction,code=self.read_code_from_file())
        response = self.llm_gpt4.generate(prompts=[_input.to_string()])
        # Extract the output text from the response
        if response.generations:
            output = response.generations[0][0].text  # Accessing the first Generation object's text
            print(response.generations[0][0].text)
        else:
            raise Exception("No response from GPT-4")

        return output
    
    def update_code(self,test_file_path="TempAX3_test_file.py"):
        try:
            shutil.copy(test_file_path, self.filepath)
        except Exception as e:
            raise Exception(f"Error copying file {self.filepath} to {test_file_path}: {e}.")
    
    def pretty_print_error(self,e):
        # Formats the error message
        error_message = f"Error occurred: {type(e).__name__} - {e}"
        return error_message

    def pretty_print_modifications(self, modifications):
        # Read current code from the file
        current_code = self.read_code_from_file()
        
        # Add the header for code and modifications
        pretty_output = "CURRENT CODE:\n" + current_code + "\n\nCODE EDITS MADE:\n"
        
        # Convert the dictionary of modifications to a JSON-formatted string
        pretty_modifications_json = json.dumps(modifications, indent=4)
        
        # Concatenate the header with the current code and the JSON string of modifications
        pretty_output += pretty_modifications_json
        
        # Truncate if the output exceeds 3000 characters
        if len(pretty_output) > 3000:
            return pretty_output[:2997] + "..."
        else:
            return pretty_output


    
    def make_change_to_python_file(self,request):
        try:
            try:
                changes=self.propose_changes(request)
            except Exception as e:
                raise Exception(f"Error proposing changes for {self.filepath}: {e}.")
            try:
                modifications=self.modifications.generate_modifications(changes)
            except Exception as e:
                raise Exception(f"Error generating changes to file {self.filepath}: {e}.")
            try:
                self.update_code()
            except Exception as e:
                raise Exception(f"Error applying changes to file {self.filepath}: {e}.")
            return str(modifications)
        except Exception as e:
            pretty_error = self.pretty_print_error(e)
        





test=make_change_to_python_file("Output_file.py")
test.make_change_to_python_file("Add some example usage.")


