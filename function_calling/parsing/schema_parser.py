import json
import re

class SchemaParser:
    def __init__(self, schema):
        """
        Initialize the SchemaParser with a given tool schema.

        :param schema: JSON object representing the schema of the tools
        """
        self.schema = schema
        self.function_definitions = {}
        self.parse_schema()

    def parse_schema(self):
        """
        Parses the schema, extracting information about each function and its parameters.
        """
        for tool in self.schema:
            if tool.get("type") == "function":
                function_info = tool["function"]
                function_name = function_info["name"]
                parameters = self.parse_parameters(function_info["parameters"])
                self.function_definitions[function_name] = {
                    "description": function_info["description"],
                    "parameters": parameters
                }

    def parse_parameters(self, params_info):
        """
        Parses the parameters of a function definition.

        :param params_info: JSON object representing the parameters of a function
        :return: Parsed parameters with their attributes
        """
        parameters = {}
        for param, attributes in params_info["properties"].items():
            parameters[param] = attributes
            if "enum" in attributes:
                parameters[param]["enum"] = attributes["enum"]
            if "minimum" in attributes:
                parameters[param]["minimum"] = attributes["minimum"]
            if "maximum" in attributes:
                parameters[param]["maximum"] = attributes["maximum"]

        # Add required parameters information if present
        if "required" in params_info:
            for required_param in params_info["required"]:
                if required_param in parameters:
                    parameters[required_param]["required"] = True

        return parameters

    def get_function_definition(self, function_name):
        """
        Retrieves the definition of a specific function from the parsed schema.

        :param function_name: Name of the function to retrieve the definition for
        :return: Function definition if found, else None
        """
        return self.function_definitions.get(function_name, None)
    
    def validate_and_format_arguments(self, function_name, args):
        """
        validates the formats of arguements for a given function
        """
        function_schema = self.schema_parser.get_function_definition(function_name)

        if not function_schema:
            raise ValueError(f"No schema found for function: {function_name}")

        validated_args = {}

        for param, attributes in function_schema["parameters"].items():
            if param in args:
                # Validate and format the argument
                validated_args[param] = self.validate_argument(args[param], attributes)
            elif "required" in attributes and attributes["required"]:
                raise ValueError(f"Missing required parameter: {param}")

        # Handle extra parameters in args not defined in the schema
        for extra_param in set(args) - set(function_schema["parameters"]):
            print(f"Extra parameter ignored: {extra_param}")

        return validated_args
    

    
    def generate_regex_patterns(self, keys):
        patterns = []

        # Strict pattern
        strict_pattern = r'\{(?:\s*"' + r'",\s*"'.join(keys) + r'"\s*:\s*".+?"\s*)+\}'
        patterns.append(strict_pattern)

        # Relaxed keys pattern
        relaxed_keys_pattern = r'\{(?:\s*' + r',\s*'.join(keys) + r'\s*:\s*".+?"\s*)+\}'
        patterns.append(relaxed_keys_pattern)

        # Relaxed comma pattern
        relaxed_comma_pattern = r'\{(?:\s*' + r',\s*'.join(keys) + r'\s*:\s*".+?"\s*,?\s*)+\}'
        patterns.append(relaxed_comma_pattern)

        # Unquoted values pattern
        unquoted_values_pattern = r'\{(?:\s*' + r',\s*'.join(keys) + r'\s*:\s*(?:.+?|"?.+?"?)\s*,?\s*)+\}'
        patterns.append(unquoted_values_pattern)

        return patterns
    
    def construct_json(self,match, keys):
        """
        Reconstructs a JSON structure from a regex match and a list of keys.

        Parameters:
        - match: A regex match object containing matched groups.
        - keys: A list of keys expected in the JSON object.

        Returns:
        A reconstructed JSON object.
        """
        json_object = {}
        for key in keys:
            # Extract value for each key from the match object
            # This assumes that the regex pattern named its capture groups after the keys
            value = match.group(key)

            # Convert the extracted value to a JSON-compatible format
            # This may involve stripping quotes, converting numeric values, etc.
            if value is not None:
                # Remove extra quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]

                # Attempt to convert numeric values
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    pass  # Keep the value as-is if it's not a valid number

            json_object[key] = value

    
    def apply_lenient_strategies(self, raw_input, keys, schema_parser, function_name):
        regex_patterns = self.generate_regex_patterns(keys)
        for pattern in regex_patterns:
            matches = re.finditer(pattern, raw_input)
            for match in matches:
                try:
                    reconstructed_json = self.reconstruct_json(match, keys)
                    validated_json = schema_parser.validate_and_format_arguments(function_name, reconstructed_json)
                    return json.dumps(validated_json)  # Convert to JSON string
                except ValueError:
                    continue
        raise ValueError("Unable to parse and validate input") 
    
    def lenient_json_parse(raw_input, schema_parser, function_name):
        try:
            parsed_json = json.loads(raw_input)
        except json.JSONDecodeError:
            parsed_json = apply_lenient_strategies(raw_input)
            if not parsed_json:
                raise ValueError("Unable to parse input as JSON")

        validated_json = schema_parser.validate_and_format_arguments(function_name, parsed_json)
        return validated_json
