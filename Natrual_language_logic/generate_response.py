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


class ResponseGenerator:
    def __init__(self,llm_model):
        self.llm_model = llm_model
        self.schema_generator = SchemaGenerator(llm_model)
        self.generated_model = None
    
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
        schema_json = self.schema_generator.produce_draft_7_schema(request).to_json()
        schema_dict = json.loads(schema_json)
        schema_dict = self.wrap_root_in_object(schema_dict)

        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_input:
            json.dump(schema_dict, temp_input)
            temp_input.flush()
            
            output_file = Path(temp_input.name).with_suffix('.py')

            # Run datamodel-codegen as a Python module
            subprocess.run([
                'python', '-m', 'datamodel_code_generator',
                '--input', temp_input.name,
                '--input-file-type', 'jsonschema',
                '--output', str(output_file)
                # Removed '--base-class' option to use default BaseModel
            ], check=True)

            # Dynamically import the generated Pydantic model
            spec = importlib.util.spec_from_file_location("generated_module", output_file)
            generated_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(generated_module)

            # Find the first Pydantic model in the generated module
            for attribute_name in dir(generated_module):
                attribute = getattr(generated_module, attribute_name)
                if issubclass(attribute, BaseModel):
                    self.generated_model = attribute
                    break

        return self.generated_model

    def construct_template(self):
        # Construct the prompt
        prompt = PromptTemplate(
            template="Respond to this qeury in the desired format: \n{query}\n",
            input_variables=["query"]
        )
        return prompt
    
        
    def generate_response(self, request):
        self.load_schema_to_pydantic(request)
        # Construct the query
        prompt = self.construct_template()
        # Make request
        _input = prompt.format_prompt(query=request)
        print(_input.to_string())

        # Generate the response
        response = self.llm_model.generate(prompts=[_input.to_string()])
        
        # Extract the output text from the response
        output = response.generations[0][0].text if response.generations else ""
        print(output)
        
        if self.generated_model:
            try:
                # Parse the output using the generated Pydantic model
                parsed_output = self.generated_model.parse_raw(output)
                return parsed_output
            except ValidationError as e:
                print(f"Failed to parse output: {e}")
                # Additional error handling or fixing logic
        else:
            print("No generated model available for parsing.")
        return None