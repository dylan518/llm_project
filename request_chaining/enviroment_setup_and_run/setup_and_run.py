import os
import subprocess
import sys

ENV_NAME = "myenv"
REQUIREMENTS_FILE = "requirements.txt"
IMPORTS_FILE = "import.txt"


def run_command(command, capture_output=True):
    result = subprocess.run(command,
                            capture_output=capture_output,
                            text=True,
                            shell=True)
    if result.stderr:
        print(f"Error executing command: {command}")
        print(result.stderr)
    return result.stdout


def create_virtual_env():
    if not os.path.exists(ENV_NAME):
        print(f"Using Python interpreter at: {sys.executable}")
        print("Attempting to create virtual environment...")
        run_command(f"{sys.executable} -m venv {ENV_NAME}")
        if os.path.exists(ENV_NAME):
            print(f"Successfully created {ENV_NAME}")
        else:
            print(f"Failed to create {ENV_NAME}")


def get_installed_packages():
    venv_python = os.path.join(ENV_NAME, 'bin', 'python')
    output = run_command(f"{venv_python} -m pip freeze")
    print(
        set(package.split('==')[0].lower() for package in output.splitlines()))
    return set(
        package.split('==')[0].lower() for package in output.splitlines())


def get_required_packages():
    with open(REQUIREMENTS_FILE, 'r') as f:
        return set(line.strip().lower() for line in f)


def install_missing_packages(missing_packages):
    venv_python = os.path.join(ENV_NAME, 'bin', 'python')
    for package in missing_packages:
        try:
            print(f"Installing {package}...")
            run_command(f"{venv_python} -m pip install {package}",
                        capture_output=False)
        except Exception as e:
            print(f"Failed to install {package}. Error: {e}")


def execute_imports():
    with open(IMPORTS_FILE, 'r') as f:
        imports = f.readlines()

    for line in imports:
        try:
            exec(line)
        except Exception as e:
            print(f"Failed to execute {line.strip()}. Error: {e}")


def run_script(script_name):
    venv_python = os.path.join(ENV_NAME, 'bin', 'python')
    subprocess.run([venv_python, script_name])


def setup_and_run():
    create_virtual_env()

    installed_packages = get_installed_packages()
    required_packages = get_required_packages()
    missing_packages = required_packages - installed_packages

    if missing_packages:
        install_missing_packages(missing_packages)

    execute_imports()

    if len(sys.argv) > 1:
        script_to_run = sys.argv[1]
        run_script(script_to_run)
    else:
        print("No script provided to run.")


if __name__ == "__main__":
    main()
