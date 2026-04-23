import os
import openai
from dotenv import load_dotenv

class LLMHandler:
    def __init__(self):
        load_dotenv()
        self.provider = os.getenv("LLM_PROVIDER", "openai").lower()
        print("DEBUG: LLM_PROVIDER is", self.provider)  # Debug print
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")

    def complete(self, prompt):
        if self.provider == "openai":
            return self._openai_complete(prompt)
        elif self.provider == "openrouter":
            return self._openrouter_complete(prompt)
        else:
            raise ValueError("Unsupported LLM provider.")

    def _openai_complete(self, prompt):
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY not set.")
        openai.api_key = self.openai_key
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=256,
            temperature=0.3
        )
        return response.choices[0].message['content'].strip()

    def _openrouter_complete(self, prompt):
        import requests
        if not self.openrouter_key:
            raise ValueError("OPENROUTER_API_KEY not set.")
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.openrouter_key}", "Content-Type": "application/json"}
        data = {
            "model": "openai/gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 256,
            "temperature": 0.3
        }
        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        return resp.json()['choices'][0]['message']['content'].strip()
