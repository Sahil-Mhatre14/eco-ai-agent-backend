from openai import OpenAI
from app.config import Config

class NemotronClient:
    def __init__(self):
        if not Config.NVIDIA_API_KEY:
            self.client = None
        else:
            self.client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=Config.NVIDIA_API_KEY
            )
        self.model = "nvidia/llama-3.1-nemotron-70b-instruct"
    
    def chat_completion(self, messages, tools=None, tool_choice=None):
        """
        Make a chat completion request to Nemotron.
        """
        if not self.client:
            # Mock response for demo
            return self._mock_response()
        
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1  # Low temperature for consistent tool use
        }
        if tools:
            params["tools"] = tools
        if tool_choice:
            params["tool_choice"] = tool_choice
        
        response = self.client.chat.completions.create(**params)
        return response
    
    def _mock_response(self):
        """Mock response when no API key."""
        from types import SimpleNamespace
        mock_choice = SimpleNamespace()
        mock_choice.message = SimpleNamespace()
        mock_choice.message.content = '{"reply": "Mock response: Please set NVIDIA_API_KEY for real AI responses.", "scenarios": []}'
        mock_choice.message.tool_calls = None
        mock_response = SimpleNamespace()
        mock_response.choices = [mock_choice]
        return mock_response