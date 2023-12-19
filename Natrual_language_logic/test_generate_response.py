from generate_response import ResponseGenerator
from langchain_community.chat_models import ChatOpenAI
from langchain.llms import OpenAI
import os

os.environ["OPENAI_API_KEY"] = "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"
chat_model = ChatOpenAI(temperature=0, model_name='gpt-4-1106-preview')
llm_model = OpenAI(temperature=0, model_name='gpt-4-1106-preview')



test_gen=ResponseGenerator( llm_model,chat_model)
schema=(test_gen.generate("return a list of presidents of the past 20 presidents and the number of electoral votes they won as a dictionary"))
print(schema)