import sys
import os

project_directory = "/Users/dylanwilson/Documents/GitHub/llm_project"

module_directories = ["enviroment_setup_and_run"]
for dir in module_directories:
    sys.path.append(project_directory + dir)
from setup_and_run import EnvironmentManager


class TaskManager:

    def __init__(self,
                 task_file_path="self_improvement/task.txt",
                 target_file_path="self_improvement/self_improve.py"):
        self.project_directory = "/Users/dylanwilson/Documents/GitHub/llm_project"
        self.task_file_path = task_file_path
        self.target_file_path = target_file_path

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
        with open(self.target_file_path, 'w') as target_file:
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
