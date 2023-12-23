from openai import OpenAI

from langchain.agents import AgentExecutor
from langchain_core.agents import AgentFinish


agent = OpenAIAssistantRunnable.create_assistant(
    name="langchain assistant e2b tool",
    instructions="You are a personal math tutor. Write and run code to answer math questions.",
    tools=tools,
    model="gpt-4-1106-preview",
    as_agent=True,
)

from langchain_core.agents import AgentFinish


def execute_agent(agent, tools, input):
    tool_map = {tool.name: tool for tool in tools}
    response = agent.invoke(input)
    while not isinstance(response, AgentFinish):
        tool_outputs = []
        for action in response:
            tool_output = tool_map[action.tool].invoke(action.tool_input)
            print(action.tool, action.tool_input, tool_output, end="\n\n")
            tool_outputs.append(
                {"output": tool_output, "tool_call_id": action.tool_call_id}
            )
        response = agent.invoke(
            {
                "tool_outputs": tool_outputs,
                "run_id": action.run_id,
                "thread_id": action.thread_id,
            }
        )

    return response
response = execute_agent(
    agent,
    tools,
    {"content": "add 3.14 and 5.0", "thread_id": None},
)
while(True):
    next_response = execute_agent(
        agent,
        tools,
        {"content": "now add 17.241", "thread_id": response.return_values["thread_id"]},
    )