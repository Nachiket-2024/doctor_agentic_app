# ---------------------------- External Imports ----------------------------
# Import the FastMCP class to create and run an MCP server exposing tools
from fastmcp import FastMCP

# ---------------------------- Internal Imports ----------------------------
# Import centralized settings (environment variables via pydantic BaseSettings)
from .core.settings import settings

# ---------------------------- MCP Initialization ----------------------------
# Create a single shared MCP instance for the project
mcp = FastMCP(name="Doctor Agentic Tools")

# ---------------------------- Import tools after MCP creation ----------------------------
# Import all tool modules after MCP instance creation to register tools
from .mcp_tools import appointment_tools
from .mcp_tools import doctor_tools
from .mcp_tools import patient_tools
from .mcp_tools import doctor_slot_tools
from .llm import llm_tools

# ---------------------------- MCP Runner ----------------------------
# Only run the MCP server if this script is executed directly
if __name__ == "__main__":
    
    # Extract host and port from MCP_URL setting (format: http://host:port)
    host_port = settings.MCP_URL.split("//")[1].split(":")
    host = host_port[0]           # Hostname part
    port = int(host_port[1])      # Port as integer

    # Start the MCP server with the specified host and port
    mcp.run(host=host, port=port)
