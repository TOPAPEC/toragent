import os
import json
from datetime import datetime

class SolutionGenerator:
    def __init__(self, claude_interface):
        self.claude = claude_interface
        self.conclusions_file = "conclusions.json"
        self.load_conclusions()

    def load_conclusions(self):
        if os.path.exists(self.conclusions_file):
            with open(self.conclusions_file, 'r') as f:
                self.conclusions = json.load(f)
        else:
            self.conclusions = []

    def save_conclusions(self):
        with open(self.conclusions_file, 'w') as f:
            json.dump(self.conclusions, f)

    def generate_solution(self, task, test_data):
        context = self._prepare_historical_context()

        # Get code
        code_prompt = f"""Task: {task}
    Test Data: {test_data}
    Historical Context: {context}

    Generate ONLY Python code for the solution. Start with imports and provide complete implementation."""

        code = self.claude.call_claude(code_prompt)

        # Get requirements
        req_prompt = f"""
        {code}
        Based on the code above, list only Python package requirements, one per line.
    Example format:
    numpy>=1.20.0
    pandas>=1.3.0
    scikit-learn>=0.24.0"""

        requirements = self.claude.call_claude(req_prompt)

        # Get conclusions
        conclusions_prompt = """Analyze the generated solution and provide brief conclusions about:

    1. Implementation approach

    2. Expected performance

    3. Potential improvements"""

        conclusions = self.claude.call_claude(conclusions_prompt)

        return {
            'code': code,
            'requirements': requirements,
            'conclusions': conclusions
        }

    def _prepare_historical_context(self):
        if not self.conclusions:
            return "No previous conclusions available."

        recent_conclusions = self.conclusions[-3:]  # Last 3 conclusions
        context = "Recent conclusions:\n"
        for c in recent_conclusions:
            context += f"- {c['conclusions']}\n"
        return context

    def test_solution(self, code, test_data):
        output_dir = "test_outputs"
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

        # Save test data and code output
        with open(output_file, 'w') as f:
            f.write(f"Test Data:\n{test_data}\n\nOutput:\n")
            # Here we would actually run the code, for now just save it
            f.write("Code output placeholder")

        return output_file
