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
            # Get error analysis
            analysis_prompt = f"""Analyze this error in the code:

Code:
{current_code}

Error:
{error_message}

Requirements:
{requirements}


"""

            error_analysis = self.claude.call_claude(analysis_prompt + "Provide detailed error analysis and root cause.")

            # Get fixed code
            fix_prompt = f"""Based on the error analysis, provide the complete fixed code.
Output only the code, no explanations."""

            fixed_code = self.claude.call_claude(analysis_prompt + error_analysis + fix_prompt)

            # Get requirement changes
            req_prompt = """List any new package requirements needed for the fixed code.
List one requirement per line in pip format. If no new requirements needed, respond with 'No new requirements'."""

            requirement_changes = self.claude.call_claude(analysis_prompt + error_analysis + req_prompt)

            # Get debug conclusions
            conclusions_prompt = """Summarize what was fixed and what improvements were made.
Be brief and specific."""

            debug_conclusions = self.claude.call_claude(analysis_prompt + error_analysis + conclusions_prompt)

            debug_record = {
                "timestamp": datetime.now().isoformat(),
                "step": debug_steps + 1,
                "original_error": error_message,
                "analysis": error_analysis,
                "fixed_code": fixed_code,
                "requirement_changes": requirement_changes,
                "conclusions": debug_conclusions
            }

            self.history.append(debug_record)
            self.save_history()

            if debug_steps == self.max_debug_steps - 1:
                print("Maximum debug steps reached. Waiting for user input...")
                user_input = input("Continue debugging? (yes/no): ")
                if user_input.lower() != 'yes':
                    break

            current_code = fixed_code
            debug_steps += 1

            # Check if the conclusions indicate the problem is solved
            if "solved" in debug_conclusions.lower() or "fixed" in debug_conclusions.lower():
                break

        return current_code, requirement_changes.split('\n') if requirement_changes != 'No new requirements' else []
