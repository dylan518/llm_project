import openai
import time

# Initialize the client
client = openai.OpenAI()

# Define a function to create an assistant and return its ID
def create_assistant(name, instructions, tools, model):
  # Send the request to OpenAI and return the ID
  response = client.beta.assistants.create(
    name=name,
    instructions=instructions,
    tools=tools,
    model=model
  )
  return response.id

# Step 1: Create the Assistant Creator
assistant_creator = create_assistant(
  name="Assistant Creator",
  instructions="I can help you create other assistants. Tell me the name, instructions, tools, and model for the new assistant, and I'll take care of it.",
  tools=[{"type": "function", "function": {"name": "create_assistant"}}],
  model="gpt-4-1106-preview"
)

# Step 2: Create a Thread
thread = client.beta.threads.create()

# Step 3: Initialize Interaction Loop
user_message = ""  # Store user's message for processing
new_assistant_requested = False  # Flag indicating user wants a new assistant
new_assistant_info = {}  # Store information for creating the new assistant

while True:
  # Wait for 5 seconds
  time.sleep(5)

  # Check for new messages in the thread
  messages = client.beta.threads.messages.list(thread_id=thread.id)

  # Process user message
  for message in messages.data:
    if message.role == "user":
      user_message = message.content[0].text.value

  # Check if user requested a new assistant
  if "create assistant" in user_message.lower():
    new_assistant_requested = True
    user_message = ""  # Reset user message for further information

  # Check if user provided information for the new assistant
  if new_assistant_requested and any(key in user_message.lower() for key in ("name", "instructions", "tools", "model")):
    # Extract relevant information from user's message
    for key in ("name", "instructions", "tools", "model"):
      if key in user_message.lower():
        new_assistant_info[key] = user_message.split(key, 1)[1].strip()

  # Create the new assistant if requested and information provided
  if new_assistant_requested and new_assistant_info:
    # Create the assistant and update instructions
    new_assistant_id = create_assistant(**new_assistant_info)
    assistant_creator_instructions = f"I can now create assistants like your requested {new_assistant_info['name']}. Ask me to create it with specific instructions."
    client.beta.threads.messages.create(thread_id=thread.id, role="assistant", content=[assistant_creator_instructions])

    # Start a new run with updated instructions and new assistant ID
    client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_creator.id, instructions=assistant_creator_instructions)

    # Clear information for the next request and reset flags
    new_assistant_requested = False
    new_assistant_info = {}

  # Print messages based on roles
  for message in messages.data:
    print(f"{message.role.capitalize()}: {message.content[0].text.value}")

# Close the thread when finished
client.beta.threads.delete(thread_id=thread.id)

