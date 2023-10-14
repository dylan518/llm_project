class FileHandler:
    """Class to handle file operations for reading task and target file."""

    @staticmethod
    def read_file(filepath):
        try:
            with open(filepath, 'r') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading file {filepath}: {str(e)}")
            return None


def generate_and_run_tests(function_code):
    """
    Generates unit tests for the given function using GPT and runs them.
    
    Args:
    - function_code (str): The code of the function to be tested.
    
    Returns:
    - bool: True if tests pass, False otherwise.
    - str: Error message if there's an error, otherwise an empty string.
    """

    # Step 1: Send the function to GPT with a request to generate unit tests
    prompt = f"Please generate unit tests for the following function:\n{function_code}"
    messages = [{'role': 'user', 'content': prompt}]
    response = gpt_request.request_gpt4(messages, 600)
    test_code_blocks = extract_python_code(response['content'])

    if not test_code_blocks:
        return False, "Failed to generate unit tests."

    # Step 2: Extract the unit tests from GPT's response
    test_code = test_code_blocks[
        0]  # Assuming the first block contains the tests

    # Step 3: Run the unit tests and return the results
    # Dynamically create a new test suite with necessary imports
    test_suite_code = f"""
import set_up_environment
import unittest
{function_code}
{test_code}
if __name__ == '__main__':
    unittest.main()
"""
    # Save the test suite to a temporary file
    with open("temp_test_suite.py", "w") as file:
        file.write(test_suite_code)

    # Run the test suite
    result = subprocess.run(["python", "temp_test_suite.py"],
                            capture_output=True,
                            text=True)

    # Clean up the temporary file
    os.remove("temp_test_suite.py")

    # Check the results
    if result.returncode == 0:
        return True, ""
    else:
        return False, result.stderr


#shortens messages to long for gpt
def shorten_messages(messages, max_chars=50000):
    """
    Shortens the list of messages to fit within the specified character limit.
    """
    message_str = str(messages)
    while (len(message_str) >= max_chars):
        del messages[1]
        print("deletion")
    return messages


def next_iteration(messages, tokens):
    print(messages)
    time.sleep(25)
    response = gpt_request.request_gpt4(messages, tokens)
    print(parse_AI_response_and_update(response))
    return ({'role': 'assistant', 'content': response})


def get_current_code():
    """
    Retrieves the current code in self_improve.py.
    """
    try:
        with open("self_improve_simple.py", "r") as file:
            code = file.read()
        return code
    except FileNotFoundError:
        print(
            "Could not find file: `self_improve_simple.py`. Please make sure the file is in the correct directory."
        )
        return None
    except ValueError:
        print(
            "Data within `self_improve_simple.py` cannot be processed. Please verify the file content."
        )
        return None
    except Exception as e:
        print(
            f"An unknown error has occurred while reading the file: {str(e)}")
        return None


#dont change task
orig_task = f"""
As an AI model, your ongoing mission is to improve the code that calls you in 'self_improve_simple.py'. 

1. Evaluate & Strategize:  Think about how the code might be parsed and the potential impacts of adding a new Python function. Perhaps plan the additions you want to make if gpt is unlikely able to output the whole addition in one code block split into multiple. If code is already partialy implemented continue implementation.

2. Respect Constraints: Be mindful of potential challenges such as I/O size limit
s. Avoid changes that could lead to infinite loops or disrupt the main execution loop. All code outputs will be incorporated into your self-improvement loop program, and this conversation is part of that loop. **Write only one function per gpt loop**.

3. Implement Improvements: If needed, generate Python functions in this format:

```python
def example_function():
    pass
Existing functions will be replaced, and new ones added. This conversation is facilitated through the code.

Reflect & Learn: Learn from each iteration. Use feedback from previous implementations to inform future improvements.
Considerations before adding code:

IMPORTANT : Write the code in plain text format for easy analysis before writing with```python``` as it will run literally and could cause errors. Answer all these questions befor writting anything in python format.
Ensure the original functionality of the code is maintained.
Verify each line functions as intended. Go line by line and think about how the new code interacts with the existing code.
Ensure there are no syntax errors.
Make sure the code can be parsed correctly by extract_python_code(), using the python format and ensuring all code is within the body of the function.
Potential Improvement Areas:

1) Error handling
a) create a system to backup the code and restore to latests functional version

brief description of the code: This system facilitates a self-improvement loop with GPT to optimize its own code. The next_iteration function sends the current code and task to GPT, and GPT responds with suggestions to improve the code. The extract_python_code function retrieves Python code blocks from GPT's response, and the update_code function integrates these suggestions into self_improve_simple.py. The main loop in if __name__ == "__main__": continuously sends the code to GPT for feedback and applies the returned improvements. In essence, the system continuously refines its own code by consulting GPT, extracting the AI's code suggestions, and integrating them.
            """

if __name__ == "__main__":
    messages = ["temp"]
    for i in range(3):  # Run the loop for three iterations
        try:
            task = orig_task + get_current_code()
            messages[0] = {'role': 'system', 'content': task}
            print(messages)
            messages = shorten_messages(messages)
            messages.append(next_iteration(messages, 600))
            print(messages)
        except Exception as e:
            error_message = str(e)  # Get the error message as a string
            print("An error occurred:", error_message)


def backup_code(filepath='self_improve_simple.py'):
    """
    Make a secure copy of the code currently working on
    Arguments:
    filepath -- str: a string that contains the name of the file we want to backup.
    """
    backup_path = filepath + '_backup'
    shutil.copy2(filepath, backup_path)
    print(f'Backup of {filepath} created at {backup_path}')


def restore_code(filepath='self_improve_simple.py'):
    """
    Restores the code from the backup file.
    """
    if os.path.isfile(filepath):
        os.remove(filepath)
    backup_path = filepath + '_backup'
    os.rename(backup_path, filepath)
    print(f'Restored the backed up file to {filepath}.')


def parse_AI_response_and_update(response):
    """
    Parses the AI response and updates self_improve_simple.py.
    """
    try:
        backup_code()
        code_blocks = extract_python_code(response)
        if not code_blocks:
            return None
        for code in code_blocks:
            func_defs = extract_function_definitions(code)
            error_message = None
            if func_defs:
                for func_def in func_defs:
                    try:
                        tree = ast.parse(func_def)
                    except SyntaxError as e:
                        error_message = str(e).split('\n')[0]
                        break
                update_code(func_def)
            if error_message:
                raise SyntaxError(error_message)
        os.remove('self_improve_simple.py_backup')
    except Exception as e:
        error_message = str(e)
        print(f'Found an error: {error_message}')
        print('Falling back to the last backup version.')
        restore_code()


import tempfile
import os
from pydantic import BaseModel, Field, validator
import shutil
import py_compile


class CodeModification(BaseModel):
    action: str = Field(description="Action to perform: add or delete")
    line_number: int = Field(description="Line number for the action")
    code: str = Field(description="Code to add", default="")

    @validator("code", always=True)
    def validate_code_compiles(cls, code, values):
        action = values.get("action")
        if action == "add" and code:
            modifier = CodeModifier('code_file.py')
            temp_modification = cls(action=action,
                                    line_number=values.get("line_number"),
                                    code=code)

            if not modifier.check_code_compiles(temp_modification):
                error_message = "Code compilation failed after applying the modifications."
                raise ValueError(error_message)
        return code


class CodeModifier:

    def __init__(self, filepath):
        self.filepath = filepath

    def apply_modifications(self, filepath, modification):
        action = modification.action
        line_number = modification.line_number - 1  # Adjusting for 0-indexing
        code = modification.code
        with open(filepath, 'r') as file:
            lines = file.readlines()
        if action == 'delete':
            del lines[line_number]
        elif action == 'add':
            code_lines = code.split('\n')
            for index, code_line in enumerate(code_lines):
                lines.insert(line_number + index, code_line + '\n')
        with open(filepath, 'w') as file:
            file.writelines(lines)

    def check_code_compiles(self, modification):
        # Create a temporary directory to work in
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the original file to the temporary directory
            temp_file_path = os.path.join(temp_dir, "temp_file.py")
            shutil.copyfile(self.filepath, temp_file_path)

            # Apply the modifications to the temporary file
            self.apply_modifications(temp_file_path, modification)

            try:
                # Try compiling the entire temporary file
                py_compile.compile(temp_file_path, doraise=True)
                return True
            except py_compile.PyCompileError:
                return False
