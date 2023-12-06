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


def eval_python_code(code):
    try:
        exec(code)
        return True
    except Exception as e:
        log_iteration_activity([],
                               f'Error while evaluating Python code: {str(e)}')
        return False


def log_iteration_activity(messages, message_content, iteration=None, total_iterations=None):
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    iteration_info = f' (iteration {iteration} of {total_iterations})' if iteration and total_iterations else ''
    full_message = f'{timestamp}{iteration_info} - {message_content}'
    messages.append({'role': 'system', 'content': full_message})
    for message in messages:
        print(message['content'])
def log_new_messages(messages, log_file_path, last_read_position_file):
    try:
        with open(last_read_position_file, 'r') as file:
            last_read_position = int(file.read().strip())
    except (FileNotFoundError, ValueError):
        last_read_position = 0
    new_messages = []
    with open(log_file_path, 'r') as file:
        file.seek(last_read_position)
        new_messages = file.readlines()
        last_read_position = file.tell()
    for message in new_messages:
        messages.append({'role': 'assistant', 'content': message.strip()})
    with open(last_read_position_file, 'w') as file:
        file.write(str(last_read_position))


def append_new_log_messages(messages):
    log_file_path = '/Users/dylanwilson/Documents/GitHub/llm_project/self_improvement/iteration_log.log'
    last_read_position_file = '/Users/dylanwilson/Documents/GitHub/llm_project/self_improvement/last_read_position.txt'
    log_new_messages(messages, log_file_path, last_read_position_file)


def read_file(filepath):
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except Exception as e:
        log_iteration_activity(
            [], f'An error occurred while reading the file: {str(e)}')
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
        python_code_blocks = []
        block_start = None

        lines = gpt_output.split('\n')
        for i, line in enumerate(lines):
            if '```python' in line and block_start is None:
                block_start = i
            elif '```' in line and block_start is not None:
                code_block = '\n'.join(lines[block_start + 1:i])
                python_code_blocks.append(code_block.strip())
                block_start = None

        print(python_code_blocks)
        return python_code_blocks

    except Exception as e:
        error_message = f"An error occurred while extracting Python code: {str(e)}"
        print(error_message)
        # Assuming log_iteration_activity is defined elsewhere
        log_iteration_activity([], error_message)
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


#updates code in self_improve.py
def update_code(func, target_file):
    try:
        tree = ast.parse(func)
        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                with open(target_file, 'r') as file:
                    data = file.readlines()
                func_start = None
                func_end = None
                indent_level = None
                for (index, line) in enumerate(data):
                    stripped = line.lstrip()
                    indent = len(line) - len(stripped)
                    if stripped.startswith(f'def {func_name}'):
                        func_start = index
                        indent_level = indent
                    elif func_start is not None and indent <= indent_level and stripped:
                        func_end = index
                        break
                if func_start is not None:
                    existing_func_snippet = ''.join(data[func_start:func_end])
                    snippet_length = len(existing_func_snippet)
                    if snippet_length > 20:
                        existing_func_snippet_start = existing_func_snippet[:
                                                                            10]
                        existing_func_snippet_end = existing_func_snippet[-10:]
                        log_iteration_activity(
                            [],
                            f'Replacing function: {existing_func_snippet_start}...{existing_func_snippet_end}'
                        )
                    else:
                        log_iteration_activity(
                            [], f'Replacing function: {existing_func_snippet}')
                    data[func_start:func_end] = [func + '\n']
                else:
                    snippet_length = len(func)
                    if snippet_length > 20:
                        log_iteration_activity(
                            [],
                            f'Adding new function: {func[:10]}...{func[-10:]}')
                    else:
                        log_iteration_activity([],
                                               f'Adding new function: {func}')
                    insert_index = 0
                    for (i, line) in enumerate(data):
                        if line.startswith('import ') or line.startswith(
                                'from '):
                            insert_index = i + 1
                    data.insert(insert_index, '\n' + func + '\n')
                new_func_snippet_start = func[:10]
                new_func_snippet_end = func[-10:]
                log_iteration_activity(
                    [],
                    f'New/Updated function: {new_func_snippet_start}...{new_func_snippet_end}'
                )
                with open(target_file, 'w') as file:
                    file.writelines(data)
    except Exception as e:
        print(f'An error occurred while updating the code: {str(e)}')


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


def restore_code(file):
    """
    Restores the code from the backup file.
    """
    filepath = file
    backup_path = filepath + '_backup'

    # Check if the backup file exists
    if os.path.isfile(backup_path):
        # Remove the original file if it exists
        if os.path.isfile(filepath):
            os.remove(filepath)

        # Rename the backup file to the original file name
        os.rename(backup_path, filepath)
        print(f'Restored the backed up file to {filepath}.')
    else:
        print(f'Backup file not found: {backup_path}')


def parse_AI_response_and_update(response, file):
    code_blocks = extract_python_code(response)
    if code_blocks:
        for code_block in code_blocks:
            if eval_python_code(code_block):
                function_definitions = extract_function_definitions(code_block)
                for function_definition in function_definitions:
                    update_code(function_definition, file)
                return True
    return False


def next_iteration(logs, file):
    log_iteration_activity(logs, 'Starting new iteration.')
    requester = LLMRequester()
    formatted_logs = [{
        'role': log['role'],
        'content': log['content']
    } for log in logs]
    response = requester.request('gpt4', formatted_logs)
    log_iteration_activity(logs, f'AI response: {response}')
    parsed_response = parse_AI_response_and_update(response, file)
    if parsed_response is None:
        log_iteration_activity(logs, 'No code blocks found in AI response.')
    else:
        log_iteration_activity(logs, 'Code blocks parsed and updated.')
    return {'role': 'assistant', 'content': response}


def main():
    print("self_improvement loop started!")
    messages = ["temp"]
    iterations = 10
    for i in range(iterations):  # Run the loop for n iterations
        try:
            target_file = get_target_file()
            print(target_file)
            task = get_task() + """
To add pyhton functions to the codefile generate Python functions in this format:

```python
def example_function():
    print('This is a simple example function that prints out a message.')
``
esnsure def is directly after python and that ```python and ``` are on their own lines. there should be nothing before or after the function. All imports will automatically be handle don't add imports
Existing functions will be replaced, and new ones added. This is the code of the target file.""" + "\n code: \n" + get_current_code(
                target_file)
            messages[0] = {'role': 'assistant', 'content': task}
            messages.append(next_iteration(messages, target_file))
        except Exception as e:
            error_message = str(e)  # Get the error message as a string
            print("An error occurred:", error_message)


main()