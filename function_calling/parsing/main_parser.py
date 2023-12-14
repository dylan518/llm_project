from schema_parser import SchemaParser
from arguement_constructor import ArgumentConstructor
from argument_constructor import ArgumentConstructor


class FunctionCallProcessor:
    def __init__(self, tools_schema):
        self.schema_parser = SchemaParser(tools_schema)
        self.argument_constructor = ArgumentConstructor(self.schema_parser)

    def process_function_calls(self, openai_output):
        processed_calls = []
        for call in openai_output:
            if call['type'] == 'function':
                function_name = call['function']['name']
                args = self.extract_function_arguments(call)
                validated_args = self.validate_function_arguments(function_name, args)
                processed_calls.append({'function': function_name, 'arguments': validated_args})
        return processed_calls

    def extract_function_arguments(self, function_call):
        raw_args = function_call['function']['arguments']
        preprocessed_args = self.argument_constructor.preprocess_text(raw_args)
        return self.argument_constructor.lenient_json_parse(preprocessed_args, self.schema_parser, function_call['function']['name'])

    def validate_function_arguments(self, function_name, args):
        return self.schema_parser.validate_and_format_arguments(function_name, args)