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
    
