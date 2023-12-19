import langchain.llms as llms
from datamodel_code_generator import InputFileType, generate
from datamodel_code_generator.parser.jsonschema import JsonSchemaParser
import json
import tempfile
import importlib.util
from generate_draft_7 import SchemaGenerator
from langchain.prompts import PromptTemplate
from pydantic import ValidationError
from pathlib import Path
import os
import subprocess
from pydantic import BaseModel
from langchain.output_parsers import OutputFixingParser, PydanticOutputParser


class ResponseGenerator:
    def __init__(self,llm_model,chat_model):
        self.llm_model = llm_model
        self.chat_model=chat_model
        self.schema_generator = SchemaGenerator(llm_model,chat_model)
        self.schema_dict=None
        self.generated_pydantic_model = None
        self.parser = None
        self.fixer = None

    def generate_parsers(self):
        if self.generated_pydantic_model:
            try:
                self.parser = PydanticOutputParser(pydantic_object=self.generated_pydantic_model)
                self.fixer = OutputFixingParser.from_llm(parser=self.parser, llm=self.chat_model)
            except Exception as e:
                print(f"Failed to generate parsers: {e}")
        else:
            print("No generated model available for parsing.")
    
    def wrap_root_in_object(self,json_schema):
        """
        Takes a JSON schema and wraps the root element in an object if it's not already an object.
        """
        # Load the schema into a dictionary if it's a string
        if isinstance(json_schema, str):
            schema_dict = json.loads(json_schema)
        else:
            schema_dict = json_schema

        # Check if the root type is already an object
        if schema_dict.get("type") == "object":
            return schema_dict

        # Extract $schema and any other top-level keys except for those defining the root type
        wrapped_schema = {key: value for key, value in schema_dict.items() if key != "type" and key != "properties" and key != "items"}
        wrapped_schema.update({
            "type": "object",
            "properties": {
                "root": {
                    "type": schema_dict.get("type"),
                    "properties": schema_dict.get("properties"),
                    "items": schema_dict.get("items")
                }
            },
            "required": ["root"]
        })

        return wrapped_schema



    def load_schema_to_pydantic(self, request):
        schema = self.schema_generator.produce_draft_7_schema(request)
        schema_json = schema.to_json()
        print(f"schema json {schema_json}")
        schema_dict = json.loads(schema_json)
        self.schema_dict = schema_dict
        schema_dict = self.wrap_root_in_object(schema_dict)

        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_input:
            json.dump(schema_dict, temp_input)
            temp_input.flush()
            
            output_file = Path(temp_input.name).with_suffix('.py')
            print(f"Generating Pydantic model from schema: {temp_input.name} -> {output_file}")

            # Run datamodel-codegen as a Python module
            subprocess.run([
                'python', '-m', 'datamodel_code_generator',
                '--input', temp_input.name,
                '--input-file-type', 'jsonschema',
                '--output', str(output_file)
            ], check=True)

            spec = importlib.util.spec_from_file_location("generated_module", str(output_file))
            generated_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(generated_module)

            # Directly access the StringListModel class
            if hasattr(generated_module, 'Model'):
                self.generated_pydantic_model = getattr(generated_module, 'Model')
            else:
                self.generated_pydantic_model = None

            return self.generated_pydantic_model

    def construct_template(self):
        # Construct the prompt
        prompt = PromptTemplate(
            template="Return the desired value for this query in the correct format.\n{format_instructions}\n{query}\n",
            input_variables=["query"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
            )
        return prompt
    
        
    def generate_response(self, request):
        print(f"Generating response for request: {request}")
        # Load the schema into a Pydantic model
        self.load_schema_to_pydantic(request)
        print(f"Loaded schema: {self.generated_pydantic_model}")
        print(f"type of schema:{type(self.generated_pydantic_model)}")

        #generate parsers
        self.generate_parsers()

        # Construct the query
        prompt = self.construct_template()

        # Make request
        _input = prompt.format_prompt(query=request)
        print(_input.to_string())

        
        # Generate the response
        response = self.llm_model.generate(prompts=[_input.to_string()])

        # Extract the output text from the response
        if response.generations:
            output = response.generations[0][0].text  # Accessing the first Generation object's text
        else:
            output = ""
        

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

    
    def generate(self,request):
        """
        Extracts internal data from a Pydantic model dump.
        If the model dump contains a 'root' key, it returns the value of 'root'.
        Otherwise, it returns the entire model dump.
        """
        pydantic_object=self.generate_response(request)
        model_dump = pydantic_object.model_dump()
        if 'root' in model_dump and isinstance(model_dump['root'], list):
            return model_dump['root']
        return model_dump
