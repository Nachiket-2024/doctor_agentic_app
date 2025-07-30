# ------------------------------------- External Imports -------------------------------------

# HTTP client to send requests to Ollama
import httpx


# ------------------------------------- Function: Query LLM -------------------------------------

# Function to call the local Ollama LLM with a prompt
async def query_llm(prompt: str, model: str = "llama3:8b-instruct-q4_K_M", base_url: str = "http://localhost:11434") -> str | None:
    """
    Send a prompt to the local LLM (Ollama) and return the response.

    Args:
        prompt (str): The user prompt or message to send to the LLM.
        model (str): Model name to query. Default is llama3:8b-instruct.
        base_url (str): URL where Ollama is running.

    Returns:
        str | None: The generated response text, or None if an error occurs.
    """

    # Wrap the request in a try-except block to catch errors
    try:
        # Create an asynchronous HTTP client context
        async with httpx.AsyncClient() as client:
            # Send a POST request to Ollama's /api/generate endpoint with the prompt and model
            response = await client.post(
                url=f"{base_url}/api/generate",
                json={
                    "model": model,         # The model to use (e.g., llama3:8b-instruct)
                    "prompt": prompt,       # The input prompt to send
                    "stream": False         # We disable streaming for now (response comes as a block)
                },
                timeout=30.0               # Timeout after 30 seconds
            )

            # Raise an HTTP exception if response status is not 2xx
            response.raise_for_status()

            # Extract and return the generated response text
            return response.json()["response"]

    # Handle any exceptions during the request
    except Exception as e:
        # Log the error to the console
        print(f"Error querying LLM: {e}")

        # Return None to indicate failure
        return None
