import json
import os
from datetime import datetime

class LoopLogger:
    DEFAULT_LOG_LEVEL = "INFO"

    def __init__(self, filepath, max_file_size=5000000, max_logs_per_loop=100):
        self.filepath = filepath
        self.max_file_size = max_file_size
        self.max_logs_per_loop = max_logs_per_loop
        self.data = self._load_logs()
        self._create_new_loop()

    def _load_logs(self):
        try:
            with open(self.filepath, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"current_loop": None, "loops": {}}

    def _save_logs(self):
        with open(self.filepath, 'w') as file:
            json.dump(self.data, file, indent=4)

    def _create_new_loop(self):
        new_loop_name = f"loop_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.data["loops"][new_loop_name] = {"logs": [], "static_variables": {}, "current_iteration": 1}
        self.data["current_loop"] = new_loop_name
        self.add_log(message="New loop started", loop_name=new_loop_name)
        self._save_logs()

    def _trim_logs(self, loop_name):
        if len(self.data["loops"][loop_name]["logs"]) > self.max_logs_per_loop:
            self.data["loops"][loop_name]["logs"] = self.data["loops"][loop_name]["logs"][-self.max_logs_per_loop:]

    def add_log(self, message, level=None, loop_name=None, iteration=None):
        loop_name = loop_name or self.data["current_loop"]
        iteration = iteration or self.data["loops"][loop_name].get("current_iteration", 1)
        level = level or self.DEFAULT_LOG_LEVEL
        log_entry = {
            "timestamp": datetime.now().isoformat(), 
            "level": level, 
            "iteration": iteration,
            "message": message
        }
        self.data["loops"][loop_name]["logs"].append(log_entry)
        self._trim_logs(loop_name)
        self._save_logs()

    def new_iteration(self, loop_name=None):
        loop_name = loop_name or self.data["current_loop"]
        if "current_iteration" in self.data["loops"][loop_name]:
            self.data["loops"][loop_name]["current_iteration"] += 1
        else:
            self.data["loops"][loop_name]["current_iteration"] = 1
        self.add_log(message="New iteration started", loop_name=loop_name)
        self._save_logs()

    def get_logs(self, loop_name=None):
        loop_name = loop_name or self.data["current_loop"]
        return self.data["loops"].get(loop_name, {}).get("logs", [])

    def set_static_variable(self, variable, value, loop_name=None):
        loop_name = loop_name or self.data["current_loop"]
        self.data["loops"][loop_name]["static_variables"][variable] = value
        self._save_logs()

    def get_static_variable(self, variable, loop_name=None):
        loop_name = loop_name or self.data["current_loop"]
        return self.data["loops"].get(loop_name, {}).get("static_variables", {}).get(variable)

    def get_current_loop(self):
        return self.data["current_loop"]

    def create_new_loop(self):
        self._create_new_loop()
