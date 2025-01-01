import json
from datetime import datetime

class AnalysisModule:
    def __init__(self, claude_interface):
        self.claude = claude_interface
        self.analysis_history_file = "analysis_history.json"
        self.load_history()

    def load_history(self):
        try:
            with open(self.analysis_history_file, 'r') as f:
                self.history = json.load(f)
        except FileNotFoundError:
            self.history = []

    def save_history(self):
        with open(self.analysis_history_file, 'w') as f:
            json.dump(self.history, f)

    def analyze_iteration(self, current_code, current_output, previous_analyses):
        prompt = f"""Analyze the tourist chatbot iteration:

Current Code:
{current_code}

Current Output:
{current_output}

Previous Analyses:
{json.dumps(previous_analyses[-3:] if previous_analyses else [], indent=2)}

Please provide:

1. Database quality assessment (cities coverage, attraction details)

2. RAG implementation effectiveness

3. Preference analysis accuracy

4. Recommendation relevance for each test query

5. Improvement/regression compared to previous iterations

6. Tuning recommendations

Format the response as JSON with these keys."""

        analysis = self.claude.call_claude(prompt)
        try:
            analysis_dict = json.loads(analysis)
        except json.JSONDecodeError:
            # Fallback to asking Claude to fix the format
            fix_prompt = f"Please format the previous response as valid JSON. Previous response: {analysis}"
            analysis = self.claude.call_claude(fix_prompt)
            analysis_dict = json.loads(analysis)

        analysis_record = {
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis_dict
        }
        
        self.history.append(analysis_record)
        self.save_history()

        return analysis_dict
