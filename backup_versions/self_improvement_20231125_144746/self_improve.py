import os
import sys
import subprocess
import re
import ast
import shutil

PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project/"
MODULE_DIRECTORIES = ["llm_requests", "running_tests"]

for directory in MODULE_DIRECTORIES:
    sys.path.append(os.path.join(PROJECT_DIRECTORY,
                                 directory))  # Use os.path.join

from llm_request import LLMRequester


def read_file(filepath):
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"An error occurred while reading the file: {str(e)}")
        return None


def get_task():
    return read_file(
        '/Users/dylanwilson/Documents/GitHub/llm_project/self_improvement/task.txt'
    )


def get_target_file():
    return read_file(
        '/Users/dylanwilson/Documents/GitHub/llm_project/self_improvement/target_file.txt'
    )


#extracts python code from gpt output
def extract_python_code(gpt_output):
    try:
        python_code_blocks = re.findall(r'```python(.*?)```', gpt_output,
                                        re.DOTALL)

        # Remove leading/trailing whitespace from each code block
        python_code_blocks = [code.strip() for code in python_code_blocks]

        print(python_code_blocks)

        return python_code_blocks
    except Exception as e:
        print(f"An error occurred while extracting Python code: {str(e)}")
        print("nothing parsed")
        return None


def extract_function_definitions(code):
    """
    Extracts function definitions from the given code.
    Returns a list of function definitions as strings.
    """
    func_defs = []

    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_defs.append(ast.unparse(node))

    return func_defs


#updates code in self_improve_simple.py
def update_code(
    func,
    target_file="/Users/dylanwilson/Documents/GitHub/llm_project/self_improvement/self_improve.py"
):
    """
    Updates the code in self_improve_simple.py with the new function.
    """
    try:
        tree = ast.parse(func)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                # Open the file and read the current code
                with open(target_file, "r") as file:
                    data = file.readlines()

                # Find the start and end of the existing function definition
                func_start = None
                func_end = None
                indent_level = None
                for index, line in enumerate(data):
                    stripped = line.lstrip()
                    indent = len(line) - len(stripped)

                    if stripped.startswith(f"def {func_name}"):
                        func_start = index
                        indent_level = indent
                    elif func_start is not None and indent <= indent_level and stripped:
                        func_end = index
                        break

                # If function exists, remove it
                if func_start is not None:
                    if func_end is not None:  # End of function found
                        data = data[:func_start] + data[func_end:]
                    else:  # End of function not found (function is at end of file)
                        data = data[:func_start]

                # Append new function at the end
                data.append('\n' + func + '\n')

                # Write the updated code back to the file
                with open(target_file, "w") as file:
                    file.writelines(data)
    except Exception as e:
        print(f"An error occurred while updating the code: {str(e)}")


def get_current_code(
    filepath='/Users/dylanwilson/Documents/GitHub/llm_project/self_improvement/self_improve.py'
):
    try:
        with open(filepath, "r") as file:
            code = file.read()
        return code
    except FileNotFoundError:
        print(
            f"Could not find file: `{filepath}`. Please make sure the file is in the correct directory."
        )
        return None


def backup_code():
    """
    Make a secure copy of the code currently working on
    Arguments:
    filepath -- str: a string that contains the name of the file we want to backup.
    """
    filepath = '/Users/dylanwilson/Documents/GitHub/llm_project/self_improvement/self_improve.py'
    backup_path = filepath + '_backup'
    shutil.copy2(filepath, backup_path)
    print(f'Backup of {filepath} created at {backup_path}')


def restore_code():
    """
    Restores the code from the backup file.
    """
    filepath = '/Users/dylanwilson/Documents/GitHub/llm_project/self_improvement/self_improve.py'
    if os.path.isfile(filepath):
        os.remove(filepath)
    backup_path = filepath + '_backup'
    os.rename(backup_path, filepath)
    print(f'Restored the backed up file to {filepath}.')


def parse_AI_response_and_update(
    response,
    file="/Users/dylanwilson/Documents/GitHub/llm_project/self_improvement/self_improve.py"
):
    """
    Parses the AI response and updates self_improve.py.
    """
    try:
        backup_code()
        code_blocks = extract_python_code(response)
        print("code blocks:\n")
        print(code_blocks)
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
                update_code(func_def, file)
            if error_message:
                raise SyntaxError(error_message)
        os.remove(
            '/Users/dylanwilson/Documents/GitHub/llm_project/self_improvement/self_improve.py_backup'
        )
    except Exception as e:
        error_message = str(e)
        print(f'Found an error: {error_message}')
        print('Falling back to the last backup version.')
        restore_code()


def next_iteration(
    messages,
    tokens,
    file="/Users/dylanwilson/Documents/GitHub/llm_project/self_improvement/self_improve.py"
):
    print(messages)
    requester = LLMRequester()
    response = requester.request("gpt4", messages, 600)
    print(parse_AI_response_and_update(response, file))
    return ({'role': 'assistant', 'content': response})


def main():
    print("self_improvement loop started!")
    messages = ["temp"]
    for i in range(3):  # Run the loop for three iterations
        try:
            target_file = get_target_file()
            print(target_file)
            task = get_task() + """
To add pyhton functions to the codefile generate Python functions in this format:

```python
def example_function():
    pass
``
esnsure def is directly after python. there should be nothing before or after the function. All imports will automatically be handle don't add imports
Existing functions will be replaced, and new ones added. This is the code of the target file.""" + "\n code: \n" + get_current_code(
                target_file)
            messages[0] = {'role': 'system', 'content': task}
            print(messages)
            messages.append(next_iteration(messages, 600, target_file))
            print(messages)
        except Exception as e:
            error_message = str(e)  # Get the error message as a string
            print("An error occurred:", error_message)


main()



def check_syntax(code):
    try:
        compile(code, '<string>', 'exec')
        return True
    except SyntaxError:
        return False




def log_error(error_message):
    error_log_path = '/Users/dylanwilson/Documents/GitHub/llm_project/self_improvement/error_log.txt'
    with open(error_log_path, 'a') as log_file:
        log_file.write(f'{error_message}\n')


def log_message(messages, new_message):
    if not isinstance(new_message, dict) or 'role' not in new_message or 'content' not in new_message:
        raise ValueError("new_message must be a dictionary with 'role' and 'content' keys")
    messages.append(new_message)
