import anthropic
import json
from datetime import datetime
import os

SYSTEM_PROMPT = """You are a precise code generation assistant. Follow these rules strictly:

1. When asked for code:
- Start with imports
- Include complete implementation
- Use only Python 3.8+ syntax
- Never include markdown code blocks or annotations
- Never include comments about code sections
- Output raw code only WITHOUT ANY FORMATTING

2. When asked for requirements:
- Use exact pip package names
- One package per line
- Include version numbers
- Format: package>=version
- No comments or explanations
- No markdown formatting

3. When asked for analysis or conclusions:
- Be concise and specific
- Use bullet points
- Focus on technical aspects
- No code snippets in analysis
- No pleasantries or explanations

4. For error analysis:
- State exact error location
- Provide specific cause
- No code snippets in analysis
- No general advice

Example requirements output:
numpy>=1.21.0
pandas>=1.3.0
scikit-learn>=0.24.0

Example analysis output:
• Memory leak in data loading
• Inefficient vector operations
• Missing error handling for empty inputs

Maintain this format strictly in all responses."""

class ClaudeInterface:
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.system_prompt = SYSTEM_PROMPT
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

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system=self.system_prompt,
            messages=[
                {"role": "user", "content": prompt}]
        )

        self.total_input_tokens += response.usage.input_tokens
        self.total_output_tokens += response.usage.output_tokens

        call_record = {
            "timestamp": datetime.now().isoformat(),
            "prompt": prompt,
            "response": response.content[0].text,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "running_total_input": self.total_input_tokens,
            "running_total_output": self.total_output_tokens
        }

        self.history.append(call_record)
        self.save_history()

        print("\nClaude Response:")
        print("=" * 50)
        print(response.content[0].text)
        print("=" * 50)
        print(f"This call: Input tokens: {response.usage.input_tokens}, Output tokens: {response.usage.output_tokens}")
        print(f"Running total: Input tokens: {self.total_input_tokens}, Output tokens: {self.total_output_tokens}")
        print(f"Total cost estimate: ${(self.total_input_tokens * 0.000003 + self.total_output_tokens * 0.000015):.4f}")

        return response.content[0].text

    def get_token_usage(self):
        return {
            "total_input": self.total_input_tokens,
            "total_output": self.total_output_tokens,
            "estimated_cost": (self.total_input_tokens * 0.000003 + self.total_output_tokens * 0.000015)
        }
