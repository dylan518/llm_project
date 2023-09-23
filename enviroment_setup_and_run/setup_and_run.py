import os
import subprocess
import sys


class EnvironmentManager:

    def __init__(self):
        self.ENV_NAME = "myenv"
        self.REQUIREMENTS_FILE = "requirements.txt"
        self.IMPORTS_FILE = "import.txt"
        self.outputs = {}

    def run_command(self, command, capture_output=True):
        result = subprocess.run(command,
                                capture_output=capture_output,
                                text=True,
                                shell=True)
        if result.stderr:
            print(f"Error executing command: {command}")
            print(result.stderr)
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
        with open(self.REQUIREMENTS_FILE, 'r') as f:
            return set(line.strip().lower() for line in f)

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
        
        # Set request limit if provided
        if request_limit:
            with open("request_limit.txt", 'w') as f:
                f.write(str(request_limit))

        # Use multiprocessing to run the script and terminate it after the time limit
        process = multiprocessing.Process(target=subprocess.run, args=([venv_python, script_name],))
        process.start()
        process.join(timeout=time_limit)
        if process.is_alive():
            print(f"Terminating {script_name} due to time limit.")
            process.terminate()
            process.join()

        # Capture the output (assuming you want to capture it after the process is terminated)
        result = subprocess.run([venv_python, script_name], capture_output=True, text=True)
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

    def main(self, scripts):
        self.setup_environment()

        for script in scripts:
            print(f"Running {script}...")
            self.run_script(script)
            print(f"Output for {script} saved.")

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
