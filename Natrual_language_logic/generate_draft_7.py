import os
import json
from typing import Optional, Union, List, Dict, Any

from pydantic import BaseModel, Field, ValidationError as PydanticValidationError, model_validator
from jsonschema import Draft7Validator, exceptions as jsonschema_exceptions

from langchain.llms import OpenAI
from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain.prompts import PromptTemplate



class SchemaProperty(BaseModel):
    # Basic JSON Schema fields
    type: Optional[Union[str, List[str]]] = None
    properties: Optional[Dict[str, 'SchemaProperty']] = None
    items: Optional[Union['SchemaProperty', List['SchemaProperty']]] = None
    additionalProperties: Union[bool, 'SchemaProperty'] = True
    required: Optional[List[str]] = None
    enum: Optional[List[Any]] = None
    const: Optional[Any] = None

    # String-specific fields
    maxLength: Optional[int] = None
    minLength: Optional[int] = None
    pattern: Optional[str] = None

    # Numeric-specific fields
    maximum: Optional[Union[int, float]] = None
    exclusiveMaximum: Optional[Union[int, float]] = None
    minimum: Optional[Union[int, float]] = None
    exclusiveMinimum: Optional[Union[int, float]] = None
    multipleOf: Optional[Union[int, float]] = None

    # Array-specific fields
    maxItems: Optional[int] = None
    minItems: Optional[int] = None
    uniqueItems: Optional[bool] = None

    # Object-specific fields
    maxProperties: Optional[int] = None
    minProperties: Optional[int] = None
    dependentRequired: Optional[Dict[str, List[str]]] = None
    dependentSchemas: Optional[Dict[str, 'SchemaProperty']] = None

    # Combining schemas
    allOf: Optional[List['SchemaProperty']] = None
    anyOf: Optional[List['SchemaProperty']] = None
    oneOf: Optional[List['SchemaProperty']] = None
    not_: Optional['SchemaProperty'] = Field(None, alias='not')

    # Annotations
    title: Optional[str] = None
    description: Optional[str] = None
    default: Optional[Any] = None
    examples: Optional[List[Any]] = None

    # Conditional subschemas (Draft-07)
    if_: Optional['SchemaProperty'] = Field(None, alias='if')
    then: Optional['SchemaProperty'] = None
    else_: Optional['SchemaProperty'] = Field(None, alias='else')

    # Draft-07 specific fields
    readOnly: Optional[bool] = None
    writeOnly: Optional[bool] = None
    contentMediaType: Optional[str] = None
    contentEncoding: Optional[str] = None
    comment: Optional[str] = Field(None, alias='$comment')

    class Config:
        extra = 'allow'
        populate_by_name = True

    def dict(self, **kwargs):
        return super().model_dump(by_alias=True, **kwargs)




class Draft7Schema(BaseModel):
    _raw_data: Optional[Dict[str, Any]] = None
    # Core keywords
    id_: Optional[str] = Field(default=None, alias='$id', format='uri-reference')
    ref_: Optional[str] = Field(None, alias='$ref')
    comment_: Optional[str] = Field(None, alias='$comment')

    # Other schema fields
    type: Optional[Union[str, List[str]]] = None
    properties: Optional[Dict[str, SchemaProperty]] = None
    additionalProperties: Union[bool, SchemaProperty] = True
    required: Optional[List[str]] = None
    patternProperties: Optional[Dict[str, 'SchemaProperty']] = None
    dependencies: Optional[Dict[str, Union[List[str], 'SchemaProperty']]] = None
    minProperties: Optional[int] = None
    maxProperties: Optional[int] = None

    # String validation keywords
    minLength: Optional[int] = None
    maxLength: Optional[int] = None
    pattern: Optional[str] = None
    format: Optional[str] = None  # Includes the new formats from Draft-07

    # Number validation keywords
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    exclusiveMinimum: Optional[float] = None
    exclusiveMaximum: Optional[float] = None
    multipleOf: Optional[float] = None

    # Array validation keywords
    items: Optional[Union['SchemaProperty', List['SchemaProperty']]] = None
    additionalItems: Union[bool, 'SchemaProperty'] = True
    minItems: Optional[int] = None
    maxItems: Optional[int] = None
    uniqueItems: Optional[bool] = None

    # Conditional subschemas (Draft-07)
    if_: Optional['SchemaProperty'] = Field(None, alias='if')
    then: Optional['SchemaProperty'] = None
    else_: Optional['SchemaProperty'] = Field(None, alias='else')

    # Draft-07 specific keywords
    readOnly: Optional[bool] = None
    writeOnly: Optional[bool] = None
    contentMediaType: Optional[str] = None
    contentEncoding: Optional[str] = None

    # Annotations
    title: Optional[str] = None
    description: Optional[str] = None
    default: Optional[Any] = None
    examples: Optional[List[Any]] = None

    # Keywords for hypermedia environments
    links: Optional[List[Dict[str, Any]]] = None  # For hyper-schema links

    # Additional class configuration
    class Config:
        extra = 'allow'
        populate_by_name = True
        json_encoders = {
            'SchemaProperty': lambda v: v.dict(by_alias=True)
        }

    def dict(self, **kwargs):
        return super().model_dump(**kwargs, by_alias=True)

    def __init__(self, **data):
        # Perform JSON Schema Draft-7 validation on the input data
        try:
            Draft7Validator.check_schema(data)
        except jsonschema_exceptions.SchemaError as e:
            raise ValueError(f"Schema validation error: {e.message}") from e

        # Call the super __init__ to handle usual Pydantic initialization
        super().__init__(**data)

    def to_json(self, **kwargs):
        return super().model_dump_json(by_alias=True, exclude_none=True, **kwargs)
    







class SchemaGenerator:

    def __init__(self,llm_model,chat_model):
        self.llm_model =llm_model
        self.chat_model=chat_model
        self.parser = PydanticOutputParser(pydantic_object=Draft7Schema)
        self.fixer = OutputFixingParser.from_llm(parser=self.parser, llm=self.chat_model)
        self.schemas = {}
        if os.path.exists("schemas.json"):
            try:
                with open("schemas.json", 'r') as file:
                    self.schemas = json.load(file)
            except json.JSONDecodeError:
                print("Warning: Failed to parse 'schemas.json'. Starting with an empty schema list.")
        else:
            self.save_schemas()  # Create an empty schemas.json file

    def save_schemas(self, request, schema):
        # Update the schemas dictionary with the new schema using the request as the key
        self.schemas[request] = schema
        print(f"Saving schema for request: {request}")

        # Write the updated schemas dictionary to the file
        with open("schemas.json", 'w') as file:
            json.dump(self.schemas, file)

    def construct_template(self):
        with open("instructions.json", 'r') as file:
            instructions = json.load(file)["draft-7"]
        # Construct the prompt
        prompt = PromptTemplate(
            template="Based off of this task: \n{query}\nRequest: \n{format_instructions}\n",
            input_variables=["query"],
            partial_variables={
                "format_instructions": instructions
            },
        )
        return prompt
    
    def generate_draft_7(self, request):
        # Construct the query
        prompt = self.construct_template()
        #make request
        _input = prompt.format_prompt(query=request)
        print(_input.to_string())

        # Generate the response
        response = self.llm_model.generate(prompts=[_input.to_string()])
        
        # Extract the output text from the response
        if response.generations:
            output = response.generations[0][0].text  # Accessing the first Generation object's text
        else:
            output = ""
            print("generation error")
        
        
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
    
    def produce_draft_7_schema(self, request):
        print(self.parser.get_format_instructions())
        # Use the request (prompt) as the key to check for existing schema
        if request in self.schemas:
            # Load the schema data from self.schemas
            schema_json = self.schemas[request]
            try:
                # Convert the JSON string back to a dictionary
                schema_data = json.loads(schema_json)
                # Create a new instance of Draft7Schema using the loaded data
                existing_schema = Draft7Schema(**schema_data)
                return existing_schema
            except PydanticValidationError as e:
                print(f"Error loading existing schema: {e}")
        else:
            # Generate a new schema if it doesn't exist for this prompt
            try:
                new_schema = self.generate_draft_7(request)
                schema_data=new_schema.to_json()
                if new_schema:
                    # Store the new schema with the request (prompt) as the key
                    self.save_schemas(request, schema_data)
                    return new_schema
                else:
                    print("Failed to generate a valid schema.")
            except Exception as e:
                print(f"Error during schema generation: {e}")

        return None


        

