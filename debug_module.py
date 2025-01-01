import json
from datetime import datetime

class DebugModule:
    def __init__(self, claude_interface):
        self.claude = claude_interface
        self.debug_history_file = "debug_history.json"
        self.load_history()
        self.max_debug_steps = 3

    def load_history(self):
        try:
            with open(self.debug_history_file, 'r') as f:
                self.history = json.load(f)
        except FileNotFoundError:
            self.history = []

    def save_history(self):
        with open(self.debug_history_file, 'w') as f:
            json.dump(self.history, f)

    def debug_code(self, code, error_message, requirements):
        debug_steps = 0
        current_code = code

        while debug_steps < self.max_debug_steps:
            prompt = f"""Debug the following code:

Code:
{current_code}

Error:
{error_message}

Requirements:
{requirements}

Please provide:

1. Analysis of the error

2. Fixed code

3. Any necessary requirement changes

4. Debug conclusions

Format the response as JSON with these keys."""

            debug_response = self.claude.call_claude(prompt)
            try:
                debug_result = json.loads(debug_response)
            except json.JSONDecodeError:
                continue

            debug_record = {
                "timestamp": datetime.now().isoformat(),
                "step": debug_steps + 1,
                "original_error": error_message,
                "debug_result": debug_result
            }

            self.history.append(debug_record)
            self.save_history()

            if debug_steps == self.max_debug_steps - 1:
                print("Maximum debug steps reached. Waiting for user input...")
                user_input = input("Continue debugging? (yes/no): ")
                if user_input.lower() != 'yes':
                    break

            current_code = debug_result["fixed_code"]
            debug_steps += 1

        return current_code, debug_result.get("requirement_changes", [])

