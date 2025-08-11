# ---------------------------- External Imports ----------------------------

# Import AsyncClient for making async HTTP calls
import httpx

# Import JSONDecodeError to handle cases where response is not valid JSON
import json

# ---------------------------- Internal Imports ----------------------------

# Import global settings (BACKEND_URL, etc.)
from ..core.settings import settings

# Import schema loader to look up endpoint details
from .schema_loader import schema_loader

# ---------------------------- Tool Executor Class ----------------------------

class ToolExecutor:
    """
    Executes API calls to the FastAPI backend based on operation_id and parameters.
    Works in coordination with SchemaLoader to dynamically handle endpoints.
    """

    def __init__(self):
        # Backend URL for backend server (from settings)
        self.backend_url = settings.BACKEND_URL

    async def execute_tool(self, operation_id: str, params: dict) -> dict:
        """
        Executes the tool (endpoint) corresponding to the given operation_id with provided parameters.
        """
        # Lookup endpoint details from the registry
        tool = schema_loader.tool_registry.get(operation_id)
        if not tool:
            raise KeyError(f"Operation ID '{operation_id}' not found in registry.")

        # Extract HTTP method and path
        method = tool["method"]
        path = tool["path"]

        # Initialize request components
        url = f"{self.backend_url}{path}"
        query_params = {}
        path_params = {}
        json_body = None

        # Separate params into query/path/body
        for name, details in tool["params"].items():
            if name == "body":
                json_body = params.get("body", {})
            elif details["in"] == "query":
                query_params[name] = params.get(name)
            elif details["in"] == "path":
                path_params[name] = params.get(name)

        # Replace placeholders in path with actual path params
        for key, value in path_params.items():
            url = url.replace(f"{{{key}}}", str(value))

        # Make async HTTP request
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                params=query_params,
                json=json_body
            )

        # Raise if request failed
        response.raise_for_status()

        try:
            # Parse JSON if possible
            return response.json()
        except json.JSONDecodeError:
            # Return raw text if not JSON
            return {"raw_response": response.text}


# ---------------------------- Global Executor Instance ----------------------------

# Singleton instance to be used across the app
tool_executor = ToolExecutor()
