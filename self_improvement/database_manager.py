import json
from datetime import datetime

class DatabaseManager:
    DEFAULT_LOG_LEVEL = "INFO"

    def __init__(self, filepath, max_file_size=5000000, max_logs_per_run=100):
        self.filepath = filepath
        self.max_file_size = max_file_size
        self.max_logs_per_run = max_logs_per_run
        self.data = self._load_logs()
        self._create_new_run()

    def _load_logs(self):
        try:
            with open(self.filepath, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"current_run": None, "runs": {}}

    def _save_logs(self):
        with open(self.filepath, 'w') as file:
            json.dump(self.data, file, indent=4)

    def _create_new_run(self):
        new_run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.data["runs"][new_run_name] = {"logs": [], "static_variables": {}}
        self.data["current_run"] = new_run_name
        self.add_log(message="New run started", run_name=new_run_name)
        self._save_logs()

    def _trim_logs(self, run_name):
        if len(self.data["runs"][run_name]["logs"]) > self.max_logs_per_run:
            self.data["runs"][run_name]["logs"] = self.data["runs"][run_name]["logs"][-self.max_logs_per_run:]

    def add_log(self, message, level=None, run_name=None):
        run_name = run_name or self.data["current_run"]
        level = level or self.DEFAULT_LOG_LEVEL
        log_entry = {
            "timestamp": datetime.now().isoformat(), 
            "level": level, 
            "message": message
        }
        self.data["runs"][run_name]["logs"].append(log_entry)
        self._trim_logs(run_name)
        self._save_logs()

    def get_last_logs(self, number_of_logs=1):
        run_name = self.get_current_run()
        if run_name not in self.data["runs"]:
            return []

        logs = self.data["runs"][run_name]["logs"]
        return logs[-number_of_logs:] if len(logs) >= number_of_logs else logs
    
    def get_logs(self, run_name=None):
        run_name = run_name or self.data["current_run"]
        return self.data["runs"].get(run_name, {}).get("logs", [])

    def set_static_variable(self, variable, value, run_name=None):
        run_name = run_name or self.data["current_run"]
        self.data["runs"][run_name]["static_variables"][variable] = value
        self._save_logs()

    def get_static_variable(self, variable, run_name=None):
        run_name = run_name or self.data["current_run"]
        return self.data["runs"].get(run_name, {}).get("static_variables", {}).get(variable)

    def get_current_run(self):
        return self.data["current_run"]

    def create_new_run(self):
        self._create_new_run()
