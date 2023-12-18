from generate_draft_7 import SchemaGenerator
from jsonschema import Draft7Validator, exceptions as jsonschema_exceptions
import json

test_gen=SchemaGenerator( "gpt-4-1106-preview","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")
schema=(test_gen.generate_draft_7("return a list of all the numbers in the list [3,7,9,12] that are greater than 5"))
# Assuming 'data' is your JSON string
data = schema.to_json()
print("validation passed and generated")

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