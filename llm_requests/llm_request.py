"""Makes API Requests to OPENAI"""
import os
import json
import time
from openai import OpenAI


class LLMRequester:
    REQUEST_LIMIT_FILE = "request_limit.txt"
    PROJECT_PATH = "/Users/dylanwilson/Documents/GitHub/llm_project/"

    def __init__(self):
        os.environ[
            "OPENAI_API_KEY"] = "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"
        self.client = OpenAI()
        self.interactions = []

    @staticmethod
    def read_request_limit():
        try:
            with open(
                    os.path.join(LLMRequester.PROJECT_PATH, "llm_requests",
                                 LLMRequester.REQUEST_LIMIT_FILE),
                    'r') as file:
                return int(file.read().strip())
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def decrement_request_limit():
        current_limit = LLMRequester.read_request_limit()
        if current_limit is not None:
            try:
                with open(
                        os.path.join(LLMRequester.PROJECT_PATH, "llm_requests",
                                     LLMRequester.REQUEST_LIMIT_FILE),
                        'w') as file:
                    file.write(str(current_limit - 1))
            except Exception as e:
                print(str(e))

    def parse_to_messages(self, prompt):
        # If it's a string, it's assumed to be from the user
        if isinstance(prompt, str):
            return [{"role": "user", "content": prompt}]

        # If it's a list, it's assumed each dictionary already has 'role' and 'content'
        elif isinstance(prompt, list) and all(
                isinstance(item, dict) and 'role' in item and 'content' in item
                for item in prompt):
            return prompt

        else:
            raise ValueError(
                "Prompt must be a string or a list of dictionaries with 'role' and 'content' keys."
            )

    def request(self, model, prompt, tokens=4000, retries=3, delay=10):
        model_map = {
            "gpt3": "gpt-3.5-turbo-1106",
            "gpt4": "gpt-4-1106-preview"
        }

        if model not in model_map:
            raise ValueError(
                "Invalid model specified. Only 'gpt-3' or 'gpt-4' are accepted."
            )

        for attempt in range(retries):
            if self.read_request_limit() <= 0:
                print("Request limit reached.")
                return None
            self.decrement_request_limit()

            try:
                messages = self.parse_to_messages(prompt)

                response = self.client.chat.completions.create(
                    model=model_map[model], messages=messages, max_tokens=4096)
                # Correctly extract the message content from the response
                method_code = response.choices[0].message.content
                if method_code:
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

    def save_solo_interaction(
        self,
        filename="/Users/dylanwilson/Documents/GitHub/llm_project/llm_request/interactions.json"
    ):
        # Saves only the last interaction
        try:
            if self.interactions:
                last_interaction = self.interactions[-1]
                with open(filename, 'w') as file:
                    json.dump(last_interaction, file)
            else:
                print("No interactions to save.")
        except Exception as e:
            print(f"Error saving interaction: {str(e)}")
