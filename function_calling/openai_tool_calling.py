
from openai import OpenAI

class OpenAIClient:
    def __init__(self):
        # Initialize the OpenAI client
        self.client = OpenAI()

    def run_conversation(self, messages, tools, tool_choice=None, model="gpt-4-turbo-1106"):
        """
        Run a conversation using the OpenAI API, forcing a specific function call if needed.
        :param messages: A list of message dictionaries.
        :param tools: A list of tool dictionaries.
        :param tool_choice: A dictionary to force a specific function call.
        :param model: The model to use for the conversation.
        :return: The response string from the API.
        """
        try:
            response = self.client.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error during OpenAI API call: {e}")
            return None