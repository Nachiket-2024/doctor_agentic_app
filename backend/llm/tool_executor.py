# ---------------------------- External Imports ----------------------------

# Import AsyncClient for making async HTTP calls
import httpx

# Import JSONDecodeError to handle cases where response is not valid JSON
import json

# Import time module to measure request duration
import time

# Import uuid to generate unique request IDs for logging
import uuid

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
    Supports passing an optional OAuth token for authenticated requests.
    """

    def __init__(self):
        # Backend URL for backend server (from settings)
        self.backend_url = settings.BACKEND_URL

    async def execute_tool(self, operation_id: str, params: dict, token: str | None = None) -> dict:
        """
        Executes the tool (endpoint) corresponding to the given operation_id with provided parameters.
        
        Args:
            operation_id: The unique operation ID for the endpoint.
            params: Parameters to send with the request.
            token: Optional OAuth Bearer token for Authorization header.
        """
        # Create unique request ID for tracing
        request_id = uuid.uuid4().hex[:8]  # short 8-char ID

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

        # Prepare headers, include Authorization if token provided
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        start_time = time.perf_counter()

        try:
            # Make async HTTP request with headers
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    params=query_params,
                    json=json_body,
                    headers=headers
                )

            # Raise if request failed
            response.raise_for_status()

            try:
                # Parse JSON if possible
                data = response.json()
                return data
            except json.JSONDecodeError:
                return {"raw_response": response.text}

        except httpx.HTTPStatusError as e:
            raise


# ---------------------------- Global Executor Instance ----------------------------

# Singleton instance to be used across the app
tool_executor = ToolExecutor()
