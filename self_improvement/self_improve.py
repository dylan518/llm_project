import os
import sys
import subprocess
import re
import ast
import shutil
import re

PROJECT_DIRECTORY = os.sep.join(
    os.path.abspath(__file__).split(os.sep)
    [:next((i for i, p in enumerate(os.path.abspath(__file__).split(os.sep))
            if 'llm_project' in p), None) +
     1]) if 'llm_project' in os.path.abspath(__file__) else None
os.environ["PROJECT_DIRECTORY"] = PROJECT_DIRECTORY

MODULE_DIRECTORIES = ["llm_requests", "running_tests"]

for directory in MODULE_DIRECTORIES:
    sys.path.append(os.path.join(PROJECT_DIRECTORY,
                                 directory))  # Use os.path.join

from llm_request import LLMRequester




def collect_logs(log_file_path, logs_start_token):
    try:
        with open(log_file_path, 'r') as log_file:
            log_content = log_file.read()

        # Use regex to find the last occurrence of logs_start_token
        matches = list(re.finditer(logs_start_token, log_content))
        if not matches:
            return 'Error: logs_start_token not found. No logs collected.'

        last_match = matches[-1]
        relevant_logs = log_content[last_match.end():]
        split_logs = re.split('(\\[INFO\\])', relevant_logs)
        grouped_logs = [
            ''.join(split_logs[i:i + 2]) for i in range(1, len(split_logs), 2)
        ]
        collected_logs = [
            log.strip() for log in grouped_logs if '[INFO]' in log
        ]
        return collected_logs

    except IOError as e:
        return f'Error: Unable to read the file - {e}'


def eval_python_code(code):
    try:
        exec(code)
        return True
    except Exception as e:
        log_iteration_activity([],
                               f'Error while evaluating Python code: {str(e)}')
        return False


def log_iteration_activity(messages,
                           message_content,
                           log_category='info',
                           current_iteration=None,
                           total_iterations=None):
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    iteration_info = ''
    if current_iteration is not None and total_iterations is not None:
        iteration_info = f'Iteration {current_iteration} of {total_iterations} - '
    log_entry = f'[{log_category.upper()}] {timestamp} - {iteration_info}{message_content}\n'
    print(os.environ.get('PROJECT_DIRECTORY'))
    log_file_path = os.path.join(os.environ.get('PROJECT_DIRECTORY'),
                                 'self_improvement/log_file.log')
    messages.append({
        'role': 'system',
        'content': log_entry.strip(),
        'category': log_category
    })
    with open(log_file_path, 'a') as log_file:
        log_file.write(log_entry)


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
    log_file_path = os.path.join(os.environ.get('PROJECT_DIRECTORY'),
                                 'self_improvement/log_file.log')
    with open(log_file_path, 'r') as file:
        new_messages = file.readlines()
    for message in new_messages:
        messages.append({'role': 'assistant', 'content': message.strip()})


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
        os.path.join(os.environ.get('PROJECT_DIRECTORY'),
                     'self_improvement/task.txt'))


def get_target_file():
    return read_file(
        os.path.join(os.environ.get('PROJECT_DIRECTORY'),
                     'self_improvement/target_file.txt'))


def get_usage():
    return read_file(
        os.path.join(os.environ.get('PROJECT_DIRECTORY'),
                     'self_improvement/usage.txt'))


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


def get_current_code(filepath):
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
    filepath = os.path.join(os.environ.get('PROJECT_DIRECTORY'),
                            'self_improvement/self_improve.py')
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
    code_updated = False
    try:
        backup_code()
        code_blocks = extract_python_code(response)
        if not code_blocks:
            log_iteration_activity([], 'No code blocks found in AI response.')
            return None
        for code in code_blocks:
            func_defs = extract_function_definitions(code)
            if func_defs:
                for func_def in func_defs:
                    try:
                        ast.parse(func_def)
                        update_code(func_def, file)
                        code=get_current_code(file)
                        if eval_python_code(func_def):
                            code_updated = True
                        else:
                            restore_code(file)
                            continue
                    except SyntaxError as e:
                        log_iteration_activity(
                            [],
                            f'Syntax error in function definition: {e.text}')
                        restore_code(file)
                        return False
        if code_updated:
            if os.path.exists(file + '_backup'):
                os.remove(file + '_backup')
            log_iteration_activity([], 'Code blocks parsed and updated.')
            return True
        else:
            log_iteration_activity([],
                                   'No new code blocks were found or added.')
            return False
    except Exception as e:
        log_iteration_activity([], f'Found an error: {str(e)}')
        restore_code(file)
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
    return {'role': 'system', 'content': response}


def main():
    start_token = 'Self-improvement loop started!'
    log_iteration_activity([], start_token)
    messages = []
    iterations = 6
    for i in range(iterations):
        log_iteration_activity([],
                               'Starting iteration',
                               current_iteration=i + 1,
                               total_iterations=iterations)
        try:
            logs_collected = collect_logs(
                os.path.join(os.environ.get('PROJECT_DIRECTORY'),
                             'self_improvement/log_file.log'), start_token)
            for log in logs_collected:
                messages.append({'role': 'system', 'content': log})
            target_file = get_target_file()
            task = get_task() + get_usage() + '\n code: \n' + get_current_code(
                target_file)
            messages.append({'role': 'system', 'content': task})
            iteration_result = next_iteration(messages, target_file)
            messages.append(iteration_result)
        except Exception as e:
            error_message = str(e)
            log_iteration_activity([],
                                   f'An error occurred: {error_message}',
                                   current_iteration=i + 1,
                                   total_iterations=iterations)


main()