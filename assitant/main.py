from openai import OpenAI
from Lang2Logic.generator import 


class CoreAssistant:
    def __init__(self, api_key, model="gpt-4-1106-preview"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.assistant_id = None

    def create_assistant(self, name, description, instructions, tools, file_ids=[]):
        """
        Create a new assistant with the specified configuration.
        """
        assistant = self.client.beta.assistants.create(
            name=name,
            description=description,
            instructions=instructions,
            model=self.model,
            tools=tools,
            file_ids=file_ids
        )
        self.assistant_id = assistant.id

    def create_thread(self, initial_messages):
        """
        Create a new thread with initial messages.
        """
        thread = self.client.beta.threads.create(messages=initial_messages)
        return thread.id

    def add_message_to_thread(self, thread_id, role, content, file_ids=[]):
        """
        Add a message to an existing thread.
        """
        message = self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role=role,
            content=content,
            file_ids=file_ids
        )
        return message.id

    def run_thread(self, thread_id):
        """
        Execute a run on a specific thread.
        """
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id
        )
        return run.id

    def get_run_status(self, thread_id, run_id):
        """
        Retrieve the status of a specific run.
        """
        run = self.client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )
        return run.status

    def retrieve_message(self, thread_id, message_id):
        """
        Retrieve a specific message from a thread.
        """
        message = self.client.beta.threads.messages.retrieve(
            thread_id=thread_id,
            message_id=message_id
        )
        return message.content