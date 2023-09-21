import shutil
import tester
import datetime
import os
import multiprocessing
from setup_environment import setup_and_run

TARGET_DIR = "self_improvement"
REQUEST_LIMIT_FILE = os.path.join("llm_requests", "request_limit.txt")
TASK_FILE = os.path.join(TARGET_DIR, "task.txt")
TARGET_PATH = "target_code.py"
BACKUP_DIR = "backup_versions"
LAST_GOOD_VERSION = "last_good_version.txt"
VERSION_LOG = "version_log.txt"
LOCAL_TASK = "self_improve_task.txt"


def set_task_instructions():
    with open(LOCAL_TASK, "r") as task_file:
        task_content = task_file.read()

    with open(os.path.join(TARGET_DIR, "self_improve.py"), "r") as code_file:
        code_content = code_file.read()

    combined_content = task_content + "\n\n" + code_content

    with open(TASK_FILE, "w") as combined_file:
        combined_file.write(combined_content)


def backup_directory():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(BACKUP_DIR, f"self_improvement_{timestamp}")
    shutil.copytree(TARGET_DIR, backup_path)
    return backup_path


def restore_directory(backup_path):
    if os.path.exists(TARGET_DIR):
        shutil.rmtree(TARGET_DIR)
    shutil.copytree(backup_path, TARGET_DIR)


def run_self_improve(task, time_limit, request_limit):
    # Set the task in task.txt
    with open(TASK_FILE, 'w') as file:
        file.write(task)

    # Set the request limit in request_limit.txt
    with open(REQUEST_LIMIT_FILE, 'w') as file:
        file.write(str(request_limit))

    # Use multiprocessing to run the self_improve.py script and terminate it after the time limit
    process = multiprocessing.Process(target=setup_and_run,
                                      args=(os.path.join(
                                          TARGET_DIR, "self_improve.py"), ))
    process.start()
    process.join(timeout=time_limit)
    if process.is_alive():
        print("Terminating self_improve.py due to time limit.")
        process.terminate()
        process.join()


def run_tests():
    test_results = tester.run_tests(
    )  # Assuming tester has a function to run tests and return results
    return test_results


def get_last_good_version():
    if os.path.exists(LAST_GOOD_VERSION):
        with open(LAST_GOOD_VERSION, 'r') as file:
            return file.read().strip()
    return None


def set_last_good_version(backup_path):
    with open(LAST_GOOD_VERSION, 'w') as file:
        file.write(backup_path)


def log_version(backup_path, status, tests_passed=[]):
    """Logs the version, its status, and the tests it passed/failed."""
    with open(VERSION_LOG, 'a') as file:
        file.write(
            f"{backup_path} | {status} | Tests: {', '.join(tests_passed)}\n")


def get_most_recent_version():
    """Returns the path of the most recent backup."""
    backups = sorted(os.listdir(BACKUP_DIR), reverse=True)
    if backups:
        return os.path.join(BACKUP_DIR, backups[0])
    return None


def handle_self_improve_error(backup_path):
    """Handles errors during the self-improve process."""
    last_good = get_last_good_version()
    if last_good:
        restore_code(last_good)
        log_version(backup_path, "Failed", ["run_self_improve"])
    else:
        most_recent = get_most_recent_version()
        if most_recent:
            restore_code(most_recent)


def handle_test_results(backup_path, test_results):
    """Handles the results of the tests."""
    if test_results:  # Assuming test_results is a list of passed test names
        set_last_good_version(backup_path)
        log_version(backup_path, "Passed", test_results)
    else:
        last_good = get_last_good_version()
        if last_good:
            restore_code(last_good)
            log_version(backup_path, "Failed", test_results)
        else:
            most_recent = get_most_recent_version()
            if most_recent:
                restore_code(most_recent)


def main_process():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    backup_path = backup_directory()

    try:
        set_task_instructions()  # Set the task instructions in task.txt
        run_self_improve(
            task_content, 600,
            10)  # Example time limit of 3600 seconds and request limit of 10
    except Exception as e:
        logging.error(f"Error in run_self_improve: {e}")
        handle_self_improve_error(backup_path)

    test_results = run_tests()
    handle_test_results(backup_path, test_results)


if __name__ == "__main__":
    main_process()