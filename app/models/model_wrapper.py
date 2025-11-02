import os
from typing import List, Dict
from pydantic import BaseModel, ConfigDict
import requests
from dotenv import load_dotenv

load_dotenv()


class ModelWrapper(BaseModel):
    backend: str = "openai"  # 'ollama' or 'openai'
    timeout: int = 120

    # Pydantic v2: prefer model_config with ConfigDict instead of class Config
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def chat(self, messages: List[Dict]) -> str:
        if self.backend == "ollama":
            return self._ollama_chat(messages)
        return self._openai_chat(messages)

    # --- Ollama ---
    def _ollama_chat(self, messages: List[Dict]) -> str:
        base = os.getenv("OLLAMA_BASE", "http://127.0.0.1:11434")
        url = f"{base}/v1/chat/completions"
        payload = {"model": "qwen2:7b", "messages": messages}
        r = requests.post(url, json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    # --- OpenAI ---
    def _openai_chat(self, messages: List[Dict]) -> str:
        base = os.getenv("OPENAI_BASE", "https://api.openai.com/v1")
        key = os.getenv("OPENAI_API_KEY", "")
        if not key:
            return "OPENAI_API_KEY is not set. Please set it in your environment or .env file."
        url = f"{base}/chat/completions"
        headers = {"Authorization": f"Bearer {key}"}
        payload = {"model": "gpt-4o-mini", "messages": messages}
        r = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
        r.raise_for_status()
        data = r.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")
