import os
import sys
import subprocess
import re
import ast
import shutil

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

def perform_self_tests(test_script_path):
    """
    Executes a script that contains a series of self-tests to validate the functionality of the enhanced code.

    Parameters:
    - test_script_path (str): The path to the testing script.
    
    Returns:
    - bool: True if all tests passed, False otherwise.
    """
    try:
        result = subprocess.run(['python', test_script_path], capture_output=True, text=True)
        if result.returncode == 0:
            log_iteration_activity([], 'All self-tests passed successfully.')
            return True
        else:
            log_iteration_activity([], f'Self-tests failed with message: {result.stderr}')
            return False
    except Exception as e:
        log_iteration_activity([], f'Error during self-tests execution: {e}')
        return False

def integrate_improvement_plan(plan, plan_file_path):
    """
    This function outlines an improvement plan to guide the iteration of improvements. 
    It retrieves, updates, or creates a plan for the progression of the code enhancement.

    Parameters:
    - plan (dict): A dictionary with a roadmap of planned enhancements.
    - plan_file_path (str): The path to the file where the plan is stored or will be stored.
    
    Returns:
    - dict: The updated plan with modifications or the same plan if no modifications were necessary.
    """
    try:
        if os.path.exists(plan_file_path):
            with open(plan_file_path, 'r') as plan_file:
                existing_plan = json.load(plan_file)
            existing_plan.update(plan)
            with open(plan_file_path, 'w') as plan_file:
                json.dump(existing_plan, plan_file)
            return existing_plan
        else:
            with open(plan_file_path, 'w') as plan_file:
                json.dump(plan, plan_file)
            return plan
    except json.JSONDecodeError as e:
        log_iteration_activity([], f'JSON decode error in plan file: {e}')
        return plan
    except Exception as e:
        log_iteration_activity([], f'Error integrating the improvement plan: {e}')
        return plan

def prioritize_tasks(task_file_path):
    """
    Prioritize the tasks listed in the tasks file. This helps the AI determine which improvements are more urgent or impactful.
    
    Parameters:
    - task_file_path (str): The path to the tasks file.
    
    Returns:
    - list: A prioritized list of tasks.
    """
    try:
        with open(task_file_path, 'r') as task_file:
            tasks = task_file.readlines()
        prioritized_tasks = sorted(tasks, key=len, reverse=True)
        return prioritized_tasks
    except IOError as e:
        log_iteration_activity([], f'Error reading tasks file: {e}')
        return []
    except Exception as e:
        log_iteration_activity([], f'General error while prioritizing tasks: {e}')
        return []


def collect_logs(log_file_path, logs_start_token):
    """
    Collects logs from the specified log file, only including logs after the given start token, with improved error handling.
    
    The logs are split based on occurrences of the [INFO] tag instead of being split by lines to group log messages that belong together.
    
    Parameters:
    - log_file_path (str): The path to the log file.
    - logs_start_token (str): The token that marks the beginning of relevant logs.
    
    Returns:
    - list: A list of strings containing the logs of interest or an error message if logs_start_token not found.
    """
    try:
        with open(log_file_path, 'r') as log_file:
            log_content = log_file.read()
        relevant_logs = log_content.split(logs_start_token, 1)[-1]
        if not relevant_logs:
            return 'Error: logs_start_token not found. No logs collected.'
        split_logs = re.split('(\\[INFO\\])', relevant_logs)
        grouped_logs = [''.join(split_logs[i:i + 2]) for i in range(1, len(split_logs), 2)]
        collected_logs = [log.strip() for log in grouped_logs if '[INFO]' in log]
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
    """
    Integrate the code suggestion from the AI response into the self_improve.py file.

    Parameters:
    - func (str): The function code to be added or updated in the target file.
    - target_file (str): The path to the target file that needs to be updated.
    """
    try:
        tree = ast.parse(func)
        func_name = tree.body[0].name if tree.body else None
        if not func_name:
            return 'Error: No valid function name found in the provided code.'
        with open(target_file, 'r') as file:
            target_code_lines = file.readlines()
        func_start_index = None
        func_end_index = None
        for (index, line) in enumerate(target_code_lines):
            if line.strip().startswith('def ' + func_name):
                func_start_index = index
                for end_index in range(index + 1, len(target_code_lines)):
                    if target_code_lines[end_index].strip() and (not target_code_lines[end_index].startswith('    ')):
                        func_end_index = end_index
                        break
                if not func_end_index:
                    func_end_index = len(target_code_lines)
                break
        if func_start_index is not None:
            new_code = target_code_lines[:func_start_index] + [func] + target_code_lines[func_end_index:]
            log_iteration_activity([], f'Updating existing function: {func_name}')
        else:
            new_code = target_code_lines + [func]
            log_iteration_activity([], f'Adding new function: {func_name}')
        with open(target_file, 'w') as file:
            file.writelines(new_code)
    except Exception as e:
        return f'Error updating code: {e}'
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
                        if eval_python_code(func_def):
                            update_code(func_def, file)
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
    iterations = 3
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