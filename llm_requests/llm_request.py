import os
import json
import time
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.schema.messages import HumanMessage


class LLMRequester:

    REQUEST_LIMIT_FILE = "request_limit.txt"
    PROJECT_PATH = "/Users/dylanwilson/Documents/GitHub/llm_project/"
    os.environ[
        'OPENAI_API_KEY'] = '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'

    @staticmethod
    def read_request_limit():
        try:
            with open(
                    os.path.join(LLMRequester.PROJECT_PATH + "llm_requests",
                                 LLMRequester.REQUEST_LIMIT_FILE),
                    'r') as file:
                return int(file.read().strip())
        except Exception as e:
            print(e)
            os._exit(1)

    @staticmethod
    def decrement_request_limit():
        try:
            current_limit = LLMRequester.read_request_limit()
            with open(
                    os.path.join(LLMRequester.PROJECT_PATH + "llm_requests",
                                 LLMRequester.REQUEST_LIMIT_FILE),
                    'w') as file:
                file.write(str(current_limit - 1))
        except Exception as e:
            print(str(e))
            os._exit(1)

    def __init__(self):
        self.interactions = []

        try:
            openai_key = os.environ.get("OPENAI_API_KEY")
            if not openai_key:
                raise ValueError("OPENAI_KEY environment variable not set.")
            self.llm_gpt3 = OpenAI(  # Use OpenAI class for llm_gpt3
                openai_api_key=os.environ.get('OPENAI_API_KEY'),
                temperature=0,
                model_name='gpt-3.5-turbo')

            self.llm_gpt4 = ChatOpenAI(  # Use ChatOpenAI class for llm_gpt4 if gpt-4 supports ChatModels
                openai_api_key=os.environ.get('OPENAI_API_KEY'),
                temperature=0,
                model_name='gpt-4-1106-preview')


#            print(dir(self.llm_gpt4))
        except Exception as e:
            print(f"Error initializing LLMs: {str(e)}")
            raise

    def parse_to_messages(self, prompt):
        # If it's a string, just return it
        if isinstance(prompt, str):
            return prompt

        # If it's a list, check if it's a list of strings or a list of dicts
        elif isinstance(prompt, list):
            if all(isinstance(item, str) for item in prompt):
                # It's a list of strings, join them
                combined_content = ' '.join(prompt)
                return combined_content
            elif all(
                    isinstance(item, dict) and 'content' in item
                    for item in prompt):
                # It's a list of dicts, combine the 'content' field
                combined_content = ' '.join(msg['content'] for msg in prompt)
                return combined_content
            else:
                raise ValueError(
                    "List items must be either all strings or all dicts with a 'content' key."
                )

        # If it's neither a string nor a list, raise an error
        else:
            raise ValueError(
                "Prompt must be a string, a list of strings, or a list of dicts with a 'content' key."
            )

    def request(self, model, prompt, retries=3, delay=10):
        time.sleep(1)
        for _ in range(retries):
            if self.read_request_limit() <= 0:
                print("Request limit reached. Terminating process.")
                os._exit(1)
            self.decrement_request_limit()
            try:
                combined_content = self.parse_to_messages(prompt)
                if not isinstance(combined_content, str):
                    raise TypeError("Parsed content must be a string.")
            except Exception as e:
                print("error parsing to string:")
                print(e)
            try:
                if model == "gpt3":
                    response = self.llm_gpt3.predict(combined_content)
                elif model == "gpt4":
                    response = self.llm_gpt4.predict(combined_content)
                else:
                    raise ValueError("Invalid model specified.")
                print(response)
                method_code = response

                self.interactions.append({
                    "model": model,
                    "prompt": prompt,
                    "response": method_code
                })
                return method_code
            except Exception as e:
                print(
                    f"Error on request: {str(e)}. Retrying in {delay} seconds..."
                )
                time.sleep(delay)
        print(
            f"Failed to get a response from {model} after {retries} attempts.")
        return None

    def save_interactions(self, filename="interactions.json"):
        try:
            with open(filename, 'w') as file:
                json.dump(self.interactions, file)
        except Exception as e:
            print(f"Error saving interactions: {str(e)}")

if __name__ == "__main__":
    requester = LLMRequester()
    prompt = "Translate the following English text to French: 'Hello, how are you?'"

    response_gpt3 = requester.request("gpt3", prompt, 1)
    response_gpt4 = requester.request("gpt4", prompt, 1)

    print("GPT-3.5 Response:", response_gpt3)
    print("GPT-4 Response:", response_gpt4)

    requester.save_interactions()
