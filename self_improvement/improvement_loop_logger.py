from database_manager import DatabaseManager
class IterationLogger(DatabaseManager):
    def __init__(self, filepath, max_file_size=5000000, max_logs_per_run=100):
        super().__init__(filepath, max_file_size, max_logs_per_run)
        self.current_iteration = 1
        self.iteration_key = f"iteration_{self.current_iteration}_logs"

    def new_iteration(self):
        # Save logs from the current iteration and start a new one
        self.set_static_variable(self.iteration_key, self.get_last_logs())
        self.current_iteration += 1
        self.iteration_key = f"iteration_{self.current_iteration}_logs"

    def get_iteration_logs(self, iteration=None):
        # Retrieve logs for a specific iteration
        iteration = iteration or self.current_iteration
        iteration_key = f"iteration_{iteration}_logs"
        return self.get_static_variable(iteration_key, [])

    def get_current_iteration(self):
        return self.current_iteration