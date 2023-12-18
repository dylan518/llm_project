import langchain.llms as llms
from datamodel_code_generator import InputFileType, generate
from datamodel_code_generator.parser.jsonschema import JsonSchemaParser
import json
import sys
from pydantic import BaseModel
import tempfile
import importlib.util
import os
class ResponseGenerator:
    def __init__(self,openai_key,model_name):
        self.llm_gpt = llms.OpenAI()
        self.schema_generator = schema_generator
        self.generated_model = None

    def load_schema_to_pydantic(self, request):
        # Use schema_generator to produce the schema
        schema_json = self.schema_generator.produce_draft_7_schema(request)
        
        # Create a temporary file to store the generated Pydantic model
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as temp_file:
            # Convert JSON schema to Pydantic model
            generate(
                input_=json.dumps(schema_json),
                input_filename=temp_file.name,
                input_file_type=InputFileType.JsonSchema,
                output=temp_file.name
            )

            # Import the generated model dynamically
            spec = importlib.util.spec_from_file_location("generated_model", temp_file.name)
            generated_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(generated_module)
            self.generated_model = getattr(generated_module, 'MainModel', None)
        
        return self.generated_model