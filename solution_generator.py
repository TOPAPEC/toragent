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
        # Prepare prompt with historical context
        context = self._prepare_historical_context()
        prompt = f"""Task: {task}
Test Data: {test_data}
Historical Context: {context}

Please analyze the task and generate:

1. Python code solution

2. Requirements.txt content

3. Analysis and conclusions

Format the response as JSON with keys: 'code', 'requirements', 'conclusions'"""

        response = self.claude.call_claude(prompt)
        try:
            solution = json.loads(response)
        except json.JSONDecodeError:
            # Fallback to asking Claude to fix the format
            fix_prompt = f"Please format the previous response as valid JSON with keys: 'code', 'requirements', 'conclusions'. Previous response: {response}"
            response = self.claude.call_claude(fix_prompt)
            solution = json.loads(response)

        # Save conclusions
        self.conclusions.append({
            "timestamp": datetime.now().isoformat(),
            "task": task,
            "conclusions": solution["conclusions"]
        })
        self.save_conclusions()

        return solution

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
