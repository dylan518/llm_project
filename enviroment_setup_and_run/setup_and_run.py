import os
import subprocess
import sys
import multiprocessing


class EnvironmentManager:

    def __init__(self):
        self.PROJECT_DIRECTORY = "/Users/dylanwilson/Documents/GitHub/llm_project/"
        self.ENV_NAME = "myenv"
        self.REQUIREMENTS_FILE = self.PROJECT_DIRECTORY + "/enviroment_setup_and_run/requirements.txt"
        self.IMPORTS_FILE = self.PROJECT_DIRECTORY + "/enviroment_setup_and_run/import.txt"
        self.outputs = {}

        os.chdir(self.PROJECT_DIRECTORY)

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

    def create_virtual_env(self):
        if not os.path.exists(self.ENV_NAME):
            print(f"Using Python interpreter at: {sys.executable}")
            print("Attempting to create virtual environment...")
            self.run_command(f"{sys.executable} -m venv {self.ENV_NAME}")

    def get_installed_packages(self):
        venv_python = os.path.join(self.ENV_NAME, 'bin', 'python')
        output = self.run_command(f"{venv_python} -m pip freeze")
        return set(
            package.split('==')[0].lower() for package in output.splitlines())

    def get_required_packages(self):
        try:
            with open(self.REQUIREMENTS_FILE, 'r') as f:
                return set(line.strip().lower() for line in f)

        except:
            print("cant get requirements file")

    def install_missing_packages(self, missing_packages):
        venv_python = os.path.join(self.ENV_NAME, 'bin', 'python')
        for package in missing_packages:
            self.run_command(f"{venv_python} -m pip install {package}")

    def execute_imports(self):
        with open(self.IMPORTS_FILE, 'r') as f:
            imports = f.readlines()

        for line in imports:
            try:
                exec(line)
            except Exception as e:
                print(f"Failed to execute {line.strip()}. Error: {e}")

    def run_script(self, script_name, time_limit=None, request_limit=None):
        venv_python = os.path.join(self.ENV_NAME, 'bin', 'python')
        if request_limit:
            with open("request_limit.txt", 'w') as f:
                f.write(str(request_limit))

        # Use multiprocessing to run the script and terminate it after the time limit
        process = multiprocessing.Process(target=subprocess.run,
                                          args=([venv_python, script_name], ))
        process.start()
        process.join(timeout=time_limit)
        if process.is_alive():
            print(f"Terminating {script_name} due to time limit.")
            process.terminate()
            process.join()

        # Capture the output (assuming you want to capture it after the process is terminated)
        result = subprocess.run([venv_python, script_name],
                                capture_output=True,
                                text=True)
        self.outputs[script_name] = result.stdout
        return result

    def setup_environment(self):
        self.create_virtual_env()

        installed_packages = self.get_installed_packages()
        required_packages = self.get_required_packages()
        missing_packages = required_packages - installed_packages

        if missing_packages:
            self.install_missing_packages(missing_packages)

        self.execute_imports()

    def setup_and_run(self, scripts, time_limit, request_limit):
        self.setup_environment()
        if isinstance(scripts, str):
            print(f"Running {self.PROJECT_DIRECTORY+scripts}...")
            self.run_script(scripts, time_limit, request_limit)
            print(f"Output for {scripts} saved.")
        elif isinstance(scripts, list):
            for script in scripts:
                print(f"Running {script}...")
                self.run_script(script, time_limit, request_limit)
                print(f"Output for {self.PROJECT_DIRECTORY+script} saved.")
        else:
            print("unexpected type")

        print("All scripts executed.")

    def get_output(self, script_name):
        return self.outputs.get(script_name, None)


if __name__ == "__main__":
    scripts_to_run = sys.argv[1:]
    manager = EnvironmentManager()
    manager.main(scripts_to_run)
    for script in scripts_to_run:
        print(f"Output for {script}:")
        print(manager.get_output(script))
