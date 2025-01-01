import anthropic
import json
from datetime import datetime
import os

class ClaudeInterface:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.history_file = "claude_history.json"
        self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
                self.total_input_tokens = sum(record.get('input_tokens', 0) for record in self.history)
                self.total_output_tokens = sum(record.get('output_tokens', 0) for record in self.history)
        else:
            self.history = []

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f)

    def call_claude(self, prompt):
        print("\nProposed Claude Call:")
        print("=" * 50)
        print(prompt)
        print("=" * 50)
        print(f"Current total usage: Input tokens: {self.total_input_tokens}, Output tokens: {self.total_output_tokens}")

        input("Press Enter to proceed with the call...")

        # Add explicit JSON request to the prompt
        json_prompt = prompt + "\n\nPlease ensure your response is a valid JSON object. Start your response with '{' and end with '}'."

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=4096,
                    messages=[{"role": "user", "content": json_prompt}]
                )

                response_text = response.content[0].text

                # Try to parse JSON
                try:
                    json_response = json.loads(response_text)
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to fix the response
                    fix_prompt = f"""The following response needs to be converted to valid JSON. 
                    Please format it as a JSON object with appropriate keys and values:

                    {response_text}

                    Return ONLY the JSON object, starting with '{{' and ending with '}}'."""

                    fix_response = self.client.messages.create(
                        model="claude-3-sonnet-20240229",
                        max_tokens=4096,
                        messages=[{"role": "user", "content": fix_prompt}]
                    )

                    response_text = fix_response.content[0].text
                    json_response = json.loads(response_text)  # If this fails too, we'll retry the whole thing

                # If we got here, we have valid JSON
                self.total_input_tokens += response.usage.input_tokens
                self.total_output_tokens += response.usage.output_tokens

                call_record = {
                    "timestamp": datetime.now().isoformat(),
                    "prompt": prompt,
                    "response": response_text,
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "running_total_input": self.total_input_tokens,
                    "running_total_output": self.total_output_tokens,
                    "attempt_number": attempt + 1
                }

                self.history.append(call_record)
                self.save_history()

                print("\nClaude Response:")
                print("=" * 50)
                print(response_text)
                print("=" * 50)
                print(f"This call: Input tokens: {response.usage.input_tokens}, Output tokens: {response.usage.output_tokens}")
                print(f"Running total: Input tokens: {self.total_input_tokens}, Output tokens: {self.total_output_tokens}")
                print(f"Total cost estimate: ${(self.total_input_tokens * 0.000015 + self.total_output_tokens * 0.000045):.4f}")

                return response_text

            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                print("Retrying...")
                continue


    def get_token_usage(self):
        return {
            "total_input": self.total_input_tokens,
            "total_output": self.total_output_tokens,
            "estimated_cost": (self.total_input_tokens * 0.000003 + self.total_output_tokens * 0.000015)
        }

