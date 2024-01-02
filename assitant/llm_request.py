"""Makes API Requests to OPENAI"""
import os
import json
import time
from datetime import datetime
from openai import OpenAI
OPENAI_API_KEY = ""


class LLMRequester:
    PROJECT_PATH = os.sep.join(
        os.path.abspath(__file__).split(os.sep)
        [:next((i
                for i, p in enumerate(os.path.abspath(__file__).split(os.sep))
                if 'llm_project' in p), None) +
         1]) if 'llm_project' in os.path.abspath(__file__) else None

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

    def save_solo_interaction(self, filename="interactions.json"):
        full_path = os.path.join(self.PROJECT_PATH, "llm_requests", filename)
        print(full_path)

        try:
            if self.interactions:
                last_interaction = self.interactions[-1]
                # Read existing data and append the new interaction
                try:
                    with open(full_path, 'r') as file:
                        existing_data = json.load(file)
                except FileNotFoundError:
                    existing_data = []

                existing_data.append(last_interaction)

                with open(full_path, 'w') as file:
                    json.dump(existing_data, file, indent=4)  # Pretty print
            else:
                print("No interactions to save.")
        except Exception as e:
            import traceback
            traceback.print_exc()

    def request(self, model, prompt, tokens=4000, retries=3, delay=5):
        model_map = {
            "gpt3": "gpt-3.5-turbo-1106",
            "gpt4": "gpt-4-1106-preview"
        }

        if model not in model_map:
            raise ValueError(
                "Invalid model specified. Only 'gpt-3' or 'gpt-4' are accepted."
            )

        for attempt in range(retries):        

            try:
                time.sleep(delay)
                messages = self.parse_to_messages(prompt)

                response = self.client.chat.completions.create(
                    model=model_map[model],
                    messages=messages,
                    max_tokens=tokens)
                # Correctly extract the message content from the response
                method_code = response.choices[0].message.content
                timestamp = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S")  # Format the timestamp
                self.interactions.append({
                    "model": model,
                    "messages": prompt,
                    "tokens": tokens,
                    "timestamp": timestamp,  # Include the timestamp
                    "response": method_code
                })
                if method_code:
                    self.save_solo_interaction()
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
    requester.request("gpt4", "test prompt")
