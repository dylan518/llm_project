import sys
import os

PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project"

MODULE_DIRECTORIES = ["enviroment_setup_and_run"]
for directory in MODULE_DIRECTORIES:
    sys.path.append(PROJECT_DIRECTORY + directory)
from setup_and_run import EnvironmentManager


class TaskManager:

    def __init__(self,
                 task_file_path="/self_improvement/task.txt",
                 target_file_path="/self_improvement/self_improve.py",
                 target_text="/self_improvement/target_file.txt"):
        self.PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project"
        self.task_file_path = self.PROJECT_DIRECTORY + task_file_path
        self.target_file_path = self.PROJECT_DIRECTORY + target_file_path
        self.target_text = self.PROJECT_DIRECTORY + target_text

    def load_task(self):
        """Load the current task from task.txt."""
        with open(self.task_file_path, 'r') as task_file:
            return task_file.read()

    def update_task(self, new_task):
        """Update the task in task.txt."""
        with open(self.task_file_path, 'w') as task_file:
            task_file.write(new_task)

    def get_current_task(self):
        """Return the current task."""
        return self.load_task()

    def set_target_file(self, target):
        """Set the target file in target_file.txt."""
        with open(self.target_text, 'w') as target_file:
            target_file.write(target)

    def run_self_improvement_loop(self, time_limit=None, request_limit=None):
        env_manager = EnvironmentManager()
        print(env_manager)
        env_manager.setup_and_run(self.target_file_path, time_limit,
                                  request_limit)


# Example usage:
# task_manager = TaskManager()
# current_task = task_manager.load_task()
# task_manager.update_task("New Task")
