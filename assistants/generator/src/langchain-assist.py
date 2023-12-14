from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from langchain.agents import AgentExecutor
from langchain.tools import DuckDuckGoSearchRun

tools = [DuckDuckGoSearchRun()]

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
        "content": 
        "What's the weather in Columbus today divided by 2"
    }
)

print(f"Content: {output['content']}\nOutput: {output['output']}")