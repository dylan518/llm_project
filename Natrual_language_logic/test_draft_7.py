from generate_draft_7 import SchemaGenerator
from jsonschema import Draft7Validator, exceptions as jsonschema_exceptions
import json
import os
from langchain.llms import OpenAI
os.environ["OPENAI_API_KEY"] = "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"
llm_gpt3 = OpenAI(temperature=0, model_name='gpt-4-1106-preview')
test_gen=SchemaGenerator( llm_gpt3)
schema=(test_gen.produce_schema("return a list of the name of the last 5 presidents"))
# Assuming 'data' is your JSON string
data = schema.to_json()
print("validation passed and generated")
print(data)

# Parse the JSON string to a dictionary
try:
    data_dict = json.loads(data)
except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON: {e}")

# Now validate the dictionary using Draft7Validator
try:
    Draft7Validator.check_schema(data_dict)
except jsonschema_exceptions.SchemaError as e:
    print(f"Schema validation error: {e.message}")
else:
    print("Schema is valid.")