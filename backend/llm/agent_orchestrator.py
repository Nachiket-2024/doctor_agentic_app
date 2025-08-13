# ---------------------------- External Imports ----------------------------

# JSON for structured communication with LLM
import json

# Logging for debug and error tracking
import logging

# ---------------------------- Internal Imports ----------------------------

# LLM agent to send prompts and get completions
from .llm_client import LLM_Client

# Tool executor to dynamically call FastAPI backend endpoints
from .tool_executor import tool_executor

# Schema loader to get info about available endpoints/tools
from .schema_loader import schema_loader

# ---------------------------- Logger Configuration ----------------------------

logger = logging.getLogger(__name__)

# ---------------------------- Agent Orchestrator Class ----------------------------

class AgentOrchestrator:
    """
    Main orchestrator handling interaction between LLM, schema tools, and backend API calls.
    """

    def __init__(self):
        # Instantiate LLM agent
        self.llm_agent = LLM_Client()

        # Schema loading should be done externally on app startup

    async def process_prompt(self, prompt: str, token: str | None = None) -> dict:
        """
        Process an incoming prompt:
        1) Send prompt to LLM
        2) Parse LLM response for tool invocation request
        3) Call the appropriate backend tool if needed, passing the token for auth
        4) Return combined or final result

        Args:
            prompt: User input prompt to send to LLM.
            token: Optional OAuth Bearer token to pass to backend API calls.
        """

        # Step 1: Ask the LLM for a response
        logger.debug(f"Sending prompt to LLM: {prompt}")
        llm_response = await self.llm_agent.generate_response(prompt)
        logger.debug(f"LLM response: {llm_response}")

        # Step 2: Parse LLM response for tool invocation
        try:
            response_data = json.loads(llm_response)
            tool_name = response_data.get("tool")
            tool_params = response_data.get("params", {})
        except json.JSONDecodeError:
            # Not JSON response - just return raw LLM output
            logger.info("LLM response not JSON, returning raw text")
            return {"response": llm_response}

        # Step 3: If tool requested, execute it
        if tool_name:
            logger.info(f"Invoking tool '{tool_name}' with params: {tool_params}")

            if tool_name not in schema_loader.tool_registry:
                error_msg = f"Requested tool '{tool_name}' not found in registry"
                logger.error(error_msg)
                return {"error": error_msg}

            try:
                # Pass the token to tool_executor for authenticated calls
                tool_result = await tool_executor.execute_tool(tool_name, tool_params, token=token)
            except Exception as e:
                logger.exception(f"Error executing tool '{tool_name}': {e}")
                return {"error": str(e)}

            # Step 4: Return tool output
            return {
                "tool_result": tool_result
            }

        # No tool call requested - return plain LLM response
        return {"response": llm_response}


# ---------------------------- Global Agent Instance ----------------------------

agent_orchestrator = AgentOrchestrator()
