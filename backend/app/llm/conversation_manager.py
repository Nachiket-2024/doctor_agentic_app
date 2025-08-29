# ---------------------------- Internal Imports ----------------------------
# Import MCP instance to access registered tools
from ..mcp_main import mcp

# Import asynchronous LLM client for generating responses
from .llm_client import LLMClient

# ---------------------------- Conversation Manager Class ----------------------------
# Class to manage LLM conversation sessions and allow MCP tool calls
class ConversationManager:
    """
    Manages LLM conversation sessions, keeps context, and allows calling MCP tools.
    """

    # Initialize the conversation manager with LLM client and session storage
    def __init__(self):
        # Create a new LLM client instance
        self.llm_client = LLMClient()
        # Store conversation history for each session (session_id -> list of messages)
        self.sessions: dict[str, list[dict]] = {}

    # Start a new conversation session
    async def start_session(self, session_id: str):
        """
        Initialize a new conversation session.

        Args:
            session_id (str): Unique identifier for the conversation.
        """
        # Create empty message history for the session
        self.sessions[session_id] = []

    # Add a message to a conversation session
    async def add_message(self, session_id: str, role: str, content: str):
        """
        Add a message to the conversation history.

        Args:
            session_id (str): Conversation identifier.
            role (str): Role of the sender ('user', 'assistant', or 'system').
            content (str): Text content of the message.
        """
        # If session does not exist, start it
        if session_id not in self.sessions:
            await self.start_session(session_id)
        # Append the message to the session's history
        self.sessions[session_id].append({"role": role, "content": content})

    # Generate a response from the LLM for a given session
    async def get_response(self, session_id: str) -> str:
        """
        Get LLM response based on the current conversation context.

        Args:
            session_id (str): Conversation identifier.

        Returns:
            str: Generated response from the LLM.
        """
        # Retrieve conversation history for the session
        conversation = self.sessions.get(session_id, [])
        # Convert message history into a single prompt string
        conversation_prompt = "\n".join(
            f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation
        )

        # Generate response using LLM client
        response = await self.llm_client.generate(conversation_prompt)

        # Store LLM response in the conversation history
        await self.add_message(session_id, "assistant", response)
        return response

    # Call an MCP-registered tool within the conversation
    async def call_tool(self, tool_name: str, **kwargs):
        """
        Allow the conversation to call an MCP-registered tool.

        Args:
            tool_name (str): Name of the MCP tool to call.
            **kwargs: Arguments to pass to the tool.

        Returns:
            Any: Result returned by the MCP tool.
        """
        # Retrieve the tool from MCP registry
        tool = mcp.tools.get(tool_name)
        # Raise an error if the tool is not registered
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not registered in MCP.")
        # Execute the tool asynchronously with provided arguments
        return await tool(**kwargs)
