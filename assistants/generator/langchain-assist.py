from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from langchain.agents import AgentExecutor
from langchain.tools import DuckDuckGoSearchRun, BaseTool

# Define the AssistantCreatorTool
class AssistantCreatorTool(BaseTool):
    name = "AssistantCreator"
    description = "Create a new assistant based on provided configuration"

    def _run(self, config: dict) -> OpenAIAssistantRunnable:
        # Extract the necessary fields from the config
        name = config.get('name', 'New Assistant')
        instructions = config.get('instructions', 'You are an assistant. Help the user')
        model = config.get('model', 'gpt-4-1106-preview')
        
        # Initialize a new assistant based on the extracted configuration
        new_assistant = OpenAIAssistantRunnable.create_assistant(
            name=name,
            instructions=instructions,
            tools=[],  # No tools are added to the new assistant in this basic implementation
            model=model,
            as_agent=True,
        )
        return new_assistant

# Existing setup
tools = [DuckDuckGoSearchRun(), AssistantCreatorTool()]

assistant = OpenAIAssistantRunnable.create_assistant(
    name="langchain assistant",
    instructions="You are an assistant. Help the user",
    tools=tools,
    model="gpt-4-1106-preview",
    as_agent=True,
)

agent_executor = AgentExecutor(agent=assistant, tools=tools)
output = agent_executor.invoke(
    {
        "content": "You are my oversight board assistant. Create a new assistant. This new assistant is to be my weather assistant. When asked questions about the weather, defer to this new assistant and pass it the necessary tools."
    }
)

print(f"Content: {output['content']}\nOutput: {output['output']}")
