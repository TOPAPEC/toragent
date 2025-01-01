import os
import venv
import subprocess
from datetime import datetime
import pip._internal.cli.main as pipmain

class EnvironmentManager:
    def __init__(self):
        self.base_dir = "iterations"
        os.makedirs(self.base_dir, exist_ok=True)

    def create_iteration(self, code, requirements):
        iteration_dir = os.path.join(self.base_dir, f"iteration_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(iteration_dir)

        # Save code and requirements
        with open(os.path.join(iteration_dir, "main.py"), 'w') as f:
            f.write(code)
        with open(os.path.join(iteration_dir, "requirements.txt"), 'w') as f:
            f.write(requirements)

        # Create venv
        venv.create(os.path.join(iteration_dir, "venv"), with_pip=True)

        # Install requirements using pip module
        try:
            pipmain.main(['install', '-r', os.path.join(iteration_dir, "requirements.txt")])
        except Exception as e:
            print(f"Installation error: {str(e)}")

        return iteration_dir

    def run_iteration(self, iteration_dir):
        python_path = os.path.join(iteration_dir, "venv", "bin", "python") if os.name != 'nt' else os.path.join(iteration_dir, "venv", "Scripts", "python")

        output_file = os.path.join(iteration_dir, "output.txt")

        try:
            result = subprocess.run(
                [python_path, os.path.join(iteration_dir, "main.py")],
                capture_output=True,
                text=True
            )

            with open(output_file, 'w') as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write("\nErrors:\n")
                    f.write(result.stderr)

            return output_file
        except Exception as e:
            with open(output_file, 'w') as f:
                f.write(f"Error running iteration: {str(e)}")
            return output_file
