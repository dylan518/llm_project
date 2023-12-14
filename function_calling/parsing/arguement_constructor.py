from schema_parser import SchemaParser
import json

class ArgumentConstructor:
    def __init__(self, schema_parser):
        """
        Initialize the ArgumentConstructor with a SchemaParser instance.

        :param schema_parser: An instance of SchemaParser containing parsed function definitions.
        """
        if not isinstance(schema_parser, SchemaParser):
            raise TypeError("schema_parser must be an instance of SchemaParser")

        self.schema_parser = schema_parser
    
    
    def preprocess_text(self, raw_text):
        """
        Cleans and normalizes the raw text input for JSON parsing, ensuring the presence of valid JSON structure.

        :param raw_text: A string containing the raw text input
        :return: A string containing cleaned and normalized text, if valid JSON structure is found
        """
        # Trim whitespace from the beginning and end
        cleaned_text = raw_text.strip()

        # Check for the presence of opening and closing braces of JSON object
        start_index = cleaned_text.find('{')
        end_index = cleaned_text.rfind('}')

        # Ensure both opening and closing braces are found and correctly positioned
        if start_index == -1 or end_index == -1 or end_index <= start_index:
            raise ValueError("Input text does not contain a valid JSON structure.")

        # Extract the JSON part from the text
        cleaned_text = cleaned_text[start_index:end_index + 1]

        # Additional cleaning steps can be added here if needed

        return cleaned_text
    
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

    
    def apply_lenient_strategies(self, raw_input, keys, function_name):
        regex_patterns = self.generate_regex_patterns(keys)
        for pattern in regex_patterns:
            matches = re.finditer(pattern, raw_input)
            for match in matches:
                try:
                    reconstructed_json = self.reconstruct_json(match, keys)
                    validated_json = self.validate_and_format_arguments(function_name, reconstructed_json)
                    return json.dumps(validated_json)  # Convert to JSON string
                except ValueError:
                    continue
        raise ValueError("Unable to parse and validate input") 
    
    def lenient_json_parse(self, raw_input):
        try:
            parsed_json = json.loads(raw_input)
        except json.JSONDecodeError:
            parsed_json = self.apply_lenient_strategies(raw_input,keys, function_name)
            if not parsed_json:
                raise ValueError("Unable to parse input as JSON")

        validated_json = schema_parser.validate_and_format_arguments(function_name, parsed_json)
        return validated_json

  