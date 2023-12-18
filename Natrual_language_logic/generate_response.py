import langchain.llms as llms
from datamodel_code_generator import InputFileType, generate
import json
import tempfile
import importlib.util
from generate_draft_7 import SchemaGenerator
from langchain.prompts import PromptTemplate
from pydantic import ValidationError


class ResponseGenerator:
    def __init__(self,llm_model):
        self.llm_model = llm_model
        self.schema_generator = SchemaGenerator(llm_model)
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
    
    def construct_template(self):
        # Construct the prompt
        self.generated_model.get_format_instructions()
        prompt = PromptTemplate(
            template="Based off of this task: \n{query}\nRequest: \n{format_instructions}\n",
            input_variables=["query"],
        )
        return prompt
    
    def generate_draft_7(self, request):
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