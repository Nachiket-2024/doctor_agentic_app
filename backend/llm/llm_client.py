# ---------------------------- External Imports ----------------------------
# Async HTTP client for making requests to Ollama server
import httpx

# ---------------------------- Internal Imports ----------------------------
# App settings containing configs like OLLAMA_BASE_URL, MODEL_NAME
from ..core.settings import settings

# ---------------------------- Agent Class ----------------------------
class LLM_Client:
    """
    Handles communication with the local Ollama LLM model.
    Designed to be modular so that future model providers can be swapped in easily.
    """

    def __init__(self):
        # Base URL of Ollama server (from settings)
        self.base_url = settings.OLLAMA_BASE_URL

        # Model name (from settings)
        self.model = settings.OLLAMA_MODEL

        # Sampling temperature (from settings)
        self.temperature = settings.OLLAMA_TEMPERATURE

    async def generate_response(self, prompt: str) -> str:
        """
        Send a prompt to the Ollama model and get back its generated text.
        """
        # Payload to send to Ollama
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "stream": False
        }

        # Create async HTTP client and send request
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/generate", json=payload)

        # Raise exception if Ollama returns an error
        response.raise_for_status()

        # Extract and return the generated text
        data = response.json()
        return data.get("response", "").strip()
