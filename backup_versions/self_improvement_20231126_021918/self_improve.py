import os
import sys
import subprocess
import re
import ast
import shutil

PROJECT_DIRECTORY = next((p for p in os.path.abspath(__file__).split(os.sep) if 'llm_project' in p), None)
MODULE_DIRECTORIES = ["llm_requests", "running_tests"]

for directory in MODULE_DIRECTORIES:
    sys.path.append(os.path.join(PROJECT_DIRECTORY,
                                 directory))  # Use os.path.join

from llm_request import LLMRequester

def log_iteration_activity(messages, message_content):
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f'{timestamp} - {message_content}\n'
    log_file_path = '/Users/dylan/Documents/GitHub/llm_project/self_improvement/iteration_log.log'
    with open(log_file_path, 'a') as log_file:
        log_file.write(log_entry)
    messages.append({'role': 'log', 'content': log_entry.strip()})


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
        messages.append({'role': 'log', 'content': message.strip()})
    with open(last_read_position_file, 'w') as file:
        file.write(str(last_read_position))


def append_new_log_messages(messages):
    log_file_path = '/Users/dylan/Documents/GitHub/llm_project/self_improvement/log_file.log'
    last_read_position_file = '/Users/dylan/Documents/GitHub/llm_project/self_improvement/last_read_position.txt'
    log_new_messages(messages, log_file_path, last_read_position_file)


def read_file(filepath):
    try:
        with open(filepath, 'r') as file:
            return file.read()
    except Exception as e:
        print(f"An error occurred while reading the file: {str(e)}")
        return None


def get_task():
    return read_file(
        '/Users/dylan/Documents/GitHub/llm_project/self_improvement/task.txt'
    )


def get_target_file():
    return read_file(
        '/Users/dylan/Documents/GitHub/llm_project/self_improvement/target_file.txt'
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


#updates code in self_improve.py
def update_code(func, target_file):
    """
    Updates the code in self_improve.py with the new function.
    Inserts the new function at the beginning of the file, after any import statements,
    or replaces an existing function with the same name.
    """
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
                    if func_end is not None:
                        data[func_start:func_end] = [func + '\n']
                    else:
                        data[func_start:] = [func + '\n']
                else:
                    insert_index = 0
                    for (i, line) in enumerate(data):
                        if line.startswith('import ') or line.startswith('from '):
                            insert_index = i + 1
                    data.insert(insert_index, '\n' + func + '\n')
                with open(target_file, 'w') as file:
                    file.writelines(data)
    except Exception as e:
        print(f'An error occurred while updating the code: {str(e)}')
def get_current_code(
    filepath='/Users/dylan/Documents/GitHub/llm_project/self_improvement/self_improve.py'
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
    filepath = '/Users/dylan/Documents/GitHub/llm_project/self_improvement/self_improve.py'
    backup_path = filepath + '_backup'
    shutil.copy2(filepath, backup_path)
    print(f'Backup of {filepath} created at {backup_path}')


def restore_code():
    """
    Restores the code from the backup file.
    """
    filepath = '/Users/dylan/Documents/GitHub/llm_project/self_improvement/self_improve.py'
    if os.path.isfile(filepath):
        os.remove(filepath)
    backup_path = filepath + '_backup'
    os.rename(backup_path, filepath)
    print(f'Restored the backed up file to {filepath}.')


def parse_AI_response_and_update(response, file):
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
            '/Users/dylan/Documents/GitHub/llm_project/self_improvement/self_improve.py_backup'
        )
    except Exception as e:
        error_message = str(e)
        print(f'Found an error: {error_message}')
        print('Falling back to the last backup version.')
        restore_code()


def next_iteration(messages, tokens, file):
    log_iteration_activity(messages, 'Starting new iteration.')
    requester = LLMRequester()
    response = requester.request('gpt4', messages)
    log_iteration_activity(messages, f'AI response: {response}')
    parsed_response = parse_AI_response_and_update(response, file)
    if parsed_response is None:
        log_iteration_activity(messages, 'No code blocks found in AI response.')
    else:
        log_iteration_activity(messages, 'Code blocks parsed and updated.')
    return {'role': 'assistant', 'content': response}
def main():
    print("self_improvement loop started!")
    messages = ["temp"]
    for i in range(7):  # Run the loop for three iterations
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
            messages.append(next_iteration(messages, 600, target_file))
        except Exception as e:
            error_message = str(e)  # Get the error message as a string
            print("An error occurred:", error_message)
        print(messages)


main()


def check_syntax(code):
    try:
        compile(code, '<string>', 'exec')
        return True
    except SyntaxError:
        return False
