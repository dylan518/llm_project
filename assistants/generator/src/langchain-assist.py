from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from langchain.agents import AgentExecutor
from langchain.tools import DuckDuckGoSearchRun, DynamicTool
import langchain.tools as tools
import { DynamicTool } from tools

# Function to create a new assistant
def create_new_assistant(input_dict):
    try:
        new_assistant = OpenAIAssistantRunnable.create_assistant(
            name=input_dict.get("name", "default_name"),
            instructions=input_dict.get("instructions", "Default instructions."),
            tools=tools,  # You can define a different set of tools if you want
            model=input_dict.get("model", "gpt-4-1106-preview"),
            as_agent=True
        )
        return f"Assistant '{input_dict.get('name', 'default_name')}' created successfully."
    except Exception as e:
        return str(e)

# Define the AssistantCreator tool
assistant_creator_tool = DynamicTool({
    'name': 'AssistantCreator',
    'description': 'Create a new assistant with given parameters.',
    'func': create_new_assistant
})

# Define the initial set of tools, including the AssistantCreator
tools = [
    DuckDuckGoSearchRun(),
    assistant_creator_tool
]

# Create the primary assistant
assistant = OpenAIAssistantRunnable.create_assistant(
    name="langchain assistant",
    instructions="You are an assistant designed to help the user write, edit, improve, and run code.",
    tools=tools,
    model="gpt-4-1106-preview",
    as_agent=True,
)

# Create the AgentExecutor with the assistant and tools
agent_executor = AgentExecutor(agent=assistant, tools=tools)

# Example invocation of the agent executor
input_dict = {
    "name": "new_assistant",
    "instructions": "You are a new assistant with specific capabilities.",
    "model": "gpt-4-1106-preview"
}

output = agent_executor.invoke({
    "content": input_dict
})

print(f"Output: {output['output']}")
