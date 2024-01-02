

from langchain.agents import AgentExecutor
from langchain_core.agents import AgentFinish
from langchain.tools import tool
import subprocess
import contextlib
import io
import traceback
from langchain.agents.openai_assistant import OpenAIAssistantRunnable
from langchain.memory import ConversationBufferMemory
from openai import OpenAI
from python_extraction import make_change_to_python_file

OPENAI_API_KEY = "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"

class CustomAgent():
    @tool
    def run_shell_command_on_mac(command:str)->str:
        """runs a given string in shell on mac OS and returns the output. Condensed if the output is too long."""
        try:
            result = subprocess.run(command, shell=True, check=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True)
            return f"OUTPUT: {result.stdout}"  # Command output
        except subprocess.CalledProcessError as e:
            return  f"Error:{e.stderr}"      # Error from command

    
    @tool
    def edit_python_file_from_prompt(file_name:str, change:str)->str:
        """Makes changes to a python file based off the prompt you give it by enlisting chat-gpt. Be as specific as possible with your prompt. If the file doesn't exist, it will be created."""
        editor=make_change_to_python_file(file_name)
        return editor.make_change_to_python_file(change)



class AgentRunner():
    
    def __init__(self):
        self.custom_agent=CustomAgent()
        def _handle_error(error) -> str:
            return str(error)[:50]
        self.custom_tools=[getattr(self.custom_agent, attr) for attr in dir(self.custom_agent)
                            if callable(getattr(self.custom_agent, attr)) and not attr.startswith('__')]
        memory = ConversationBufferMemory(memory_key="chat_history")
        self.agent = OpenAIAssistantRunnable.create_assistant(
            name="Complete all the tasks assigned to you by gpt",
            instructions="Work with the use to write and debugg code.",
            tools=self.custom_tools,
            model="gpt-4-1106-preview",
            as_agent=True, 
            verbose=True,
            memory=memory,
            handle_parsing_errors=_handle_error,
        )





    def execute_agent(self,agent, tools, input):
        tool_map = {tool.name: tool for tool in tools}
        response = self.agent.invoke(input)
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
    
    def main(self):
        user_input = input("Request here: ")
        response = self.execute_agent(
            self.agent,
            self.custom_tools,
            {"content": user_input},
        )
        print(response.return_values)
        while(True):
            user_input = input("Request here: ")
            next_response = self.execute_agent(
                self.agent,
                self.custom_tools,
                {"content": user_input, "thread_id": response.return_values["thread_id"]},
            )

if __name__ == "__main__":
    agent_runner = AgentRunner()
    agent_runner.main()  