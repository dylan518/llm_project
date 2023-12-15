import os
import sys
import json
import shutil
import re
import sqlite3




    
from python_extraction import ModificationGenerator
from database_mannager import Database_Mannager

def add_custom_packages_to_path():
    """
    since outside of working directory must add costum modules to path
    """
    database=Database_Mannager()
    MODULE_DIRECTORIES = ["llm_requests", "running_tests"]
    for directory in MODULE_DIRECTORIES:
        sys.path.append(os.path.join(database.get_static_variable("project_directory"),
                                    directory)) 

add_custom_packages_to_path()
from llm_request import LLMRequester




class improvement_loop:
    def __init__(self):
        self.database=Database_Mannager()
        
    def get_current_code(self):
        try:
            with open( self.database.get_static_variable('target_file'), "r") as file:
                self.database.set_static_variable('current_code', file.read())
            return None
        except FileNotFoundError:
            print(
                f"Could not find file: `{self.database.get_static_variable('target_file')}`. Please make sure the file is in the correct directory."
            )
            return None


    def format_logs_for_gpt(self):
        """
        Formats the logs for GPT-4.
        """
        try:
            logs=self.database.get_logs()
            gpt_formatted_logs = [
                {"role": "user", "content": " - ".join([f"{key}: {log[key]}" for key in log])}
                for log in logs
            ]
            return gpt_formatted_logs
        except Exception as e:
            self.database.add_log(f"Error formatting logs for GPT: {e}","ERROR")
            return None
    
    def construct_instructions(self):
        """
        Constructs the instruction for GPT-4.
        """
        instructions=""
        for var in ["task", "usage", "current_code"]:
            try:
                task+=self.database.get_static_variable(var)
            except:
                self.database.add_log(f"Error getting static variable: {var}","ERROR")
        self.database.get_static_variable("instructions",instructions)
        return instructions
        
    def next_iteration(self):
        self.database.new_iteration()
        requester = LLMRequester()
        try:
            response = requester.request('gpt4', self.format_logs_for_gpt())
        except Exception as e:
            self.database.add_log(f"Error requesting from LLM: {e}","ERROR")
        try:
            self.database.add_log( f'AI response: {response}')
            ModificationGenerator(self.database.get_static_variable("target_file"))
            modifications=str(ModificationGenerator.generate_modifications([response]))
            if modifications:
                self.database.add_log( 'Code blocks parsed and updated./n{modifications}')
            else:
                self.database.add_log('No code blocks found in AI response.')
        except Exception as e:
            self.database.add_log('Error making changes. \n Error: {e}.', "ERROR")
        return None


    def main(self):
        self.database._create_new_loop()
        for i in range(self.database.get_static_variable("iterations")):
            self.construct_instructions()


runner=improvement_loop()
runner.main()
