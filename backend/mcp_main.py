# ---------------------------- External Imports ----------------------------

# Import the FastMCP class which provides the MCP server for exposing tools
from fastmcp import FastMCP

# ---------------------------- Internal Imports ----------------------------

# Import centralized settings (loads environment variables via pydantic BaseSettings)
from .core.settings import settings

# Import all tool modules so they register their tools with the shared MCP
# Each tool file should import `mcp` from this file and attach tools to it
from .mcp_tools import appointment_tools
from .mcp_tools import doctor_tools
from .mcp_tools import patient_tools
from .mcp_tools import doctor_slot_tools

# ---------------------------- MCP Initialization ----------------------------

# Create a single shared MCP instance for the entire project
mcp = FastMCP(name="Doctor Agentic Tools")

# ---------------------------- MCP Runner ----------------------------

# Only run the MCP server if this script is executed directly
if __name__ == "__main__":
    
    # Extract host and port from MCP_URL setting (format: http://host:port)
    host_port = settings.MCP_URL.split("//")[1].split(":")
    host = host_port[0]           # Hostname part
    port = int(host_port[1])      # Port as integer

    # Start the MCP server with extracted host and port
    mcp.run(host=host, port=port)
