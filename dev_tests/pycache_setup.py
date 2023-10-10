import os
import sys

project_directory = "/Users/dylanwilson/Documents/GitHub/llm_project/"
module_directories = [
    "main", "llm_requests", "enviroment_setup_and_run", "running_tests",
    "logging", "self_improvement"
]


def add_init_files(root_directory, module_dirs):
    """Add __init__.py to specified module directories starting from root_directory."""
    for module_dir in module_dirs:
        target_dir = os.path.join(root_directory, module_dir)

        # Ensure that the directory exists
        if os.path.exists(target_dir):
            init_file = os.path.join(target_dir, '__init__.py')

            # Create __init__.py if it doesn't exist
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    # Create an empty __init__.py file
                    pass
                print(f"Added __init__.py in {target_dir}")
        else:
            print(f"Directory not found: {target_dir}")


add_init_files(project_directory, module_directories)

# Provide the path to your project's root directory
project_root = "/Users/dylanwilson/Documents/GitHub/llm_project/"
add_init_files(project_root)
