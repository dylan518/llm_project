import os
import json
import time
from langchain import OpenAI


class LLMRequester:

    REQUEST_LIMIT_FILE = "request_limit.txt"

    @staticmethod
    def read_request_limit():
        try:
            with open(LLMRequester.REQUEST_LIMIT_FILE, 'r') as file:
                return int(file.read().strip())
        except:
            print(
                "Error reading request limit or no value given. Terminating process."
            )
            os._exit(1)

    @staticmethod
    def decrement_request_limit():
        try:
            current_limit = LLMRequester.read_request_limit()
            with open(LLMRequester.REQUEST_LIMIT_FILE, 'w') as file:
                file.write(str(current_limit - 1))
        except:
            print("Error decrementing request limit. Terminating process.")
            os._exit(1)

    def __init__(self):
        self.interactions = []

        try:
            openai_key = os.environ.get("OPENAI_KEY")
            if not openai_key:
                raise ValueError("OPENAI_KEY environment variable not set.")

            self.llm_gpt3 = OpenAI(openai_api_key=str(openai_key),
                                   temperature=0,
                                   model_name='gpt-3.5-turbo')

            self.llm_gpt4 = OpenAI(openai_api_key=openai_key,
                                   temperature=0,
                                   model_name='gpt-4.0-turbo')
        except Exception as e:
            print(f"Error initializing LLMs: {str(e)}")
            raise

    def request(self, model, prompt, retries=3, delay=10):
        for _ in range(retries):
            if self.read_request_limit() <= 0:
                print("Request limit reached. Terminating process.")
                os._exit(1)
            self.decrement_request_limit()
            try:
                if model == "gpt3":
                    response = self.llm_gpt3.generate([prompt])
                elif model == "gpt4":
                    response = self.llm_gpt4.generate([prompt])
                else:
                    raise ValueError("Invalid model specified.")

                method_code = response.generations[0][0].text

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

    response_gpt3 = requester.request("gpt3", prompt)
    response_gpt4 = requester.request("gpt4", prompt)

    print("GPT-3.5 Response:", response_gpt3)
    print("GPT-4 Response:", response_gpt4)

    requester.save_interactions()
