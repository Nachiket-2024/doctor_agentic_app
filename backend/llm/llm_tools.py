# ---------------------------- External Imports ----------------------------
# Import the shared MCP instance to define and register tools
from ..mcp_main import mcp

# ---------------------------- Internal Imports ----------------------------
# Import the asynchronous LLM client class
from .llm_client import LLMClient

# ---------------------------- LLM Client Initialization ----------------------------
# Create a single shared LLM client instance for use by all MCP tools
llm_client = LLMClient()

# ---------------------------- MCP Tool: Generate Text ----------------------------
# Define MCP tool to generate text from LLM given a prompt
@mcp.tool(
    name="generate_text",  # Tool name
    description="Generate text using the LLM based on the provided prompt."  # Tool description
)
# Async function to generate text
async def generate_text_tool(prompt: str) -> str:
    """
    Generate text from LLM given an input prompt.

    Args:
        prompt (str): The text prompt to send to the LLM.

    Returns:
        str: Generated text from the LLM.
    """
    # Delegate text generation to the shared LLM client
    return await llm_client.generate(prompt)

# ---------------------------- MCP Tool: Chat with LLM ----------------------------
# Define MCP tool to simulate a conversational chat with the LLM
@mcp.tool(
    name="chat_with_llm",  # Tool name
    description="Simulate a conversational chat with the LLM given a list of messages."  # Tool description
)
# Async function to generate chat responses
async def chat_with_llm_tool(messages: list[dict]) -> str:
    """
    Generate a chat response from the LLM given a conversation context.

    Args:
        messages (list[dict]): List of messages in the format
                               {"role": "user|assistant|system", "content": "text"}.

    Returns:
        str: LLM response to the conversation.
    """
    # Convert conversation messages into a single prompt string for the LLM
    conversation_prompt = "\n".join(
        f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages
    )

    # Delegate generation to the shared LLM client
    return await llm_client.generate(conversation_prompt)
