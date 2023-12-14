from parsing.main_parser import FunctionCallProcessor
from openai_tool_calling import OpenAIClient

class MainRunner:
    def __init__(self, tools_schema, validator):
        """
        Initialize the MainRunner with required components.
        :param tools_schema: Schema for tools to be used in FunctionCallProcessor.
        :param validator: Validator class with a validate function.
        """
        self.openai_client = OpenAIClient()
        self.function_call_processor = FunctionCallProcessor(tools_schema)
        self.validator = validator

    def run(self, messages, tools):
        """
        Main method to run the entire process.
        :param messages: Messages to be processed by OpenAI.
        :param tools: Tools to be used for function calls.
        :return: Validated response or an error message.
        """
        # Step 1: Get conversation output from OpenAI
        openai_output = self.openai_client.run_conversation(messages, tools)
        if not openai_output:
            return "Error in getting response from OpenAI."

        # Step 2: Process function calls using FunctionCallProcessor
        processed_calls = self.function_call_processor.process_function_calls(openai_output)
        
        # Step 3: Validate the results
        try:
            validated_response = self.validator.validate(processed_calls)
            return validated_response
        except Exception as e:
            return f"Validation error: {e}"