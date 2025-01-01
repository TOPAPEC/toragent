import anthropic
import json
from datetime import datetime
import os

class ClaudeInterface:
    def __init__(self, api_key):
        self.client = anthropic.Client(api_key)
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.history_file = "claude_history.json"
        self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                self.history = json.load(f)
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

        input("Press Enter to proceed with the call...")

        response = self.client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        )

        self.total_input_tokens += response.usage.input_tokens
        self.total_output_tokens += response.usage.output_tokens

        call_record = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response.content[0].text,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }

        self.history.append(call_record)
        self.save_history()

        print("\nClaude Response:")
        print("=" * 50)
        print(response.content[0].text)
        print("=" * 50)
        print(f"Input tokens: {response.usage.input_tokens}")
        print(f"Output tokens: {response.usage.output_tokens}")

        return response.content[0].text

    def get_token_usage(self):
        return {
            "total_input": self.total_input_tokens,
            "total_output": self.total_output_tokens
        }

