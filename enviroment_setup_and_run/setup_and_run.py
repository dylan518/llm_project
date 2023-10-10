import os
import subprocess
import sys
import multiprocessing


class EnvironmentManager:

    def __init__(self):
        self.PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project"
        self.ENV_NAME = os.path.join(self.PROJECT_DIRECTORY, "myenv")
        self.REQUIREMENTS_FILE = os.path.join(self.PROJECT_DIRECTORY,
                                              "enviroment_setup_and_run",
                                              "requirements.txt")
        self.IMPORTS_FILE = os.path.join(self.PROJECT_DIRECTORY,
                                         "enviroment_setup_and_run",
                                         "import.txt")
        self.outputs = {}

    def set_request_limit(self, request_limit):
        request_limit_file_path = os.path.join(self.PROJECT_DIRECTORY,
                                               "llm_requests",
                                               "request_limit.txt")
        with open(request_limit_file_path, 'w') as f:
            f.write(str(request_limit))

    def upgrade_pip(self):
        command = f"{self.ENV_NAME} -m pip install --upgrade pip"
        subprocess.run(command, shell=True, check=True)

    def run_command(self, command, capture_output=True):
        result = subprocess.run(command,
                                capture_output=capture_output,
                                text=True,
                                shell=True)
        if result.stderr:
            print(f"Error executing command: {command}")
            print(result.stderr)
            print(result.stdout)
        return result.stdout

    def get_installed_packages(self):
        venv_python = os.path.join(self.ENV_NAME, 'bin', 'python')
        output = self.run_command(f"{venv_python} -m pip freeze")
        return set(
            package.split('==')[0].lower() for package in output.splitlines())

    def get_required_packages(self):
        with open(self.REQUIREMENTS_FILE, 'r') as f:
            return set(line.strip().lower() for line in f)

    def install_missing_packages(self, missing_packages):
        venv_python = os.path.join(self.ENV_NAME, 'bin', 'python')
        try:
            self.upgrade_pip()
        except:
            print("failed to upgrade pip")
        for package in missing_packages:
            print(f"Installing {package}...")
            output = self.run_command(
                f"{venv_python} -m pip install {package}")
            print(output)

    def execute_imports(self):
        venv_python = os.path.join(self.ENV_NAME, 'bin', 'python')
        with open(self.IMPORTS_FILE, 'r') as f:
            imports = f.readlines()
        for line in imports:
            command = f"{venv_python} -c '{line.strip()}'"
            result = subprocess.run(command,
                                    shell=True,
                                    text=True,
                                    capture_output=True)
            if result.stderr:
                print(
                    f"Failed to execute {line.strip()}. Error: {result.stderr}"
                )

    def create_virtual_env(self):
        if not os.path.exists(self.ENV_NAME):
            print(f"Using Python interpreter at: {sys.executable}")
            print("Attempting to create virtual environment...")
            self.run_command(f"{sys.executable} -m venv {self.ENV_NAME}")
            if not os.path.exists(self.ENV_NAME):
                print("Failed to create virtual environment.")
                return False
        print("Virtual environment created successfully.")
        return True

    def run_script(self, script_name, time_limit=None, request_limit=None):
        if request_limit:
            self.set_request_limit(request_limit)
        venv_python = os.path.join(self.ENV_NAME, 'bin',
                                   'python')  # absolute path to Python in venv
        script_path = os.path.join(self.PROJECT_DIRECTORY, script_name)
        command = f"{venv_python} {script_path}"  # updated command
        try:
            result = subprocess.run(command,
                                    shell=True,
                                    timeout=time_limit,
                                    capture_output=True,
                                    text=True)
            self.outputs[script_name] = result.stdout
        except subprocess.TimeoutExpired:
            print(f"Terminating {script_name} due to time limit.")
        except Exception as e:
            print(f"Error running {script_name}: {e}")

    def setup_environment(self):
        if not self.create_virtual_env():
            return
        installed_packages = self.get_installed_packages()
        required_packages = self.get_required_packages()
        missing_packages = required_packages - installed_packages
        if missing_packages:
            self.install_missing_packages(missing_packages)
        self.execute_imports()

    def setup_and_run(self, scripts, time_limit, request_limit):
        self.setup_environment()
        if isinstance(scripts, str):
            print(f"Running {scripts}...")
            self.run_script(scripts, time_limit, request_limit)
            print(f"Output for {scripts} saved.")
        elif isinstance(scripts, list):
            for script in scripts:
                print(f"Running {script}...")
                self.run_script(script, time_limit, request_limit)
                print(f"Output for {script} saved.")
        else:
            print("Unexpected type")
        print("All scripts executed.")

    def get_output(self, script_name):
        return self.outputs.get(script_name, None)


if __name__ == "__main__":
    scripts_to_run = sys.argv[1:]
    manager = EnvironmentManager()
    manager.setup_and_run(
        scripts_to_run, None,
        None)  # Adjust time_limit and request_limit as needed
    for script in scripts_to_run:
        print(f"Output for {script}:")
        print(manager.get_output(script))
