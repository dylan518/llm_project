from generate_response import ResponseGenerator
from langchain.llms import OpenAI
import os
os.environ["OPENAI_API_KEY"] = "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"
llm_gpt3 = OpenAI(temperature=0, model_name='gpt-4-1106-preview')
test_gen=ResponseGenerator( llm_gpt3)
schema=(test_gen.generate_response("return a list of the name of the last 5 presidents"))