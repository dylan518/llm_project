import openai
import time

# Initialize the client
client = openai.OpenAI()

# Define a function to create an assistant
def create_assistant(name, instructions, tools, model):
    return client.beta.assistants.create(
        name=name,
        instructions=instructions,
        tools=tools,
        model=model
    )


# Step 1: Create an Assistant
assistant = create_assistant(
    name="Assistant Creator",
    instructions="You can create other assistants. To do so, specify the name, instructions, tools, and model. The user will prompt you for a basic structure of other assistants you are to create and their behavior.",
    tools=[{"type": "function", "function": {"name": "create_assistant"}}],
    model="gpt-4-1106-preview"
)

# Step 2: Create a Thread
thread = client.beta.threads.create()

# Step 3: Add a Message to a Thread
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="Can you create another assistant that is instructred to be a math helper?"
)

# Step 4: Run the Assistant
run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions="Please address the user as Alex. The user has a premium account."
)

print(run.model_dump_json(indent=4))

while True:
    # Wait for 5 seconds
    time.sleep(5)  

    # Retrieve the run status
    run_status = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    print(run_status.model_dump_json(indent=4))

    # If run is completed, get messages
    if run_status.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        
        # Loop through messages and print content based on role
        for msg in messages.data:
            role = msg.role
            content = msg.content[0].text.value
            print(f"{role.capitalize()}: {content}")
        
        break