# ---------------------------- External Imports ----------------------------

# Import AsyncClient from httpx for making asynchronous HTTP requests
import httpx

# Import JSON decoding errors to handle malformed responses
import json

# ---------------------------- Internal Imports ----------------------------

# Import application settings (BACKEND_URL, etc.)
from ..core.settings import settings

# ---------------------------- Schema Loader Class ----------------------------

class SchemaLoader:
    """
    Loads, parses, and caches the OpenAPI schema for the FastAPI backend.
    Extracts endpoint details and parameter templates for LLM integration.
    """

    def __init__(self):
        # Store the OpenAPI schema after fetching
        self.openapi_schema = None

        # Registry mapping operation_id -> endpoint details
        self.tool_registry = {}

    async def fetch_openapi(self):
        """
        Fetch the OpenAPI schema from the FastAPI server.
        """
        # Compose full URL to the OpenAPI spec
        openapi_url = f"{settings.BACKEND_URL}/openapi.json"

        # Create async HTTP client to send the GET request
        async with httpx.AsyncClient() as client:
            response = await client.get(openapi_url)

        # Raise an exception if request failed
        response.raise_for_status()

        try:
            # Parse the JSON response into a Python dictionary
            self.openapi_schema = response.json()
        except json.JSONDecodeError as e:
            raise RuntimeError("Failed to parse OpenAPI schema JSON") from e

    def build_tool_registry(self):
        """
        Parse the OpenAPI schema into a registry of available tools/endpoints.
        """
        # Ensure schema is loaded
        if not self.openapi_schema:
            raise RuntimeError("OpenAPI schema not loaded. Call fetch_openapi() first.")

        # Loop through all paths in the schema
        for path, methods in self.openapi_schema.get("paths", {}).items():
            for method, details in methods.items():
                # Extract operation ID (unique identifier for endpoint)
                operation_id = details.get("operationId")
                if not operation_id:
                    continue

                # Extract parameters (query/path/body)
                params = {}
                for param in details.get("parameters", []):
                    params[param["name"]] = {
                        "in": param.get("in"),
                        "required": param.get("required", False),
                        "schema": param.get("schema", {}),
                    }

                # If requestBody exists, handle JSON schema
                if "requestBody" in details:
                    content = details["requestBody"].get("content", {})
                    if "application/json" in content:
                        schema = content["application/json"].get("schema", {})
                        params["body"] = schema

                # Store the tool metadata in registry
                self.tool_registry[operation_id] = {
                    "path": path,
                    "method": method.upper(),
                    "params": params,
                }

    def get_tool_template(self, operation_id):
        """
        Return an example payload/template for the given operation_id.
        """
        # Lookup operation_id in registry
        tool = self.tool_registry.get(operation_id)
        if not tool:
            raise KeyError(f"Operation ID '{operation_id}' not found in registry.")

        # Initialize template dict
        template = {}
        for name, details in tool["params"].items():
            if name == "body":
                # Body schema handling (set all fields to None as placeholders)
                if "properties" in details:
                    template["body"] = {
                        field: None for field in details["properties"].keys()
                    }
                else:
                    template["body"] = {}
            else:
                # Query/path params: set placeholder None
                template[name] = None

        return template


# ---------------------------- Global Loader Instance ----------------------------

# Create a singleton instance for the app
schema_loader = SchemaLoader()
