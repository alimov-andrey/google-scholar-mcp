"""Google Scholar MCP Server - Entry Point."""

from fastmcp import FastMCP

from .config import get_settings
from .clients.serpapi import SerpAPIClient
from .clients.core_api import CoreAPIClient
from .tools.scholar import register_scholar_tools
from .tools.fulltext import register_fulltext_tools

# Initialize FastMCP server
mcp = FastMCP(
    name="google-scholar-mcp",
    version="2.0.0",
)

# Initialize clients on startup
settings = None
serpapi_client = None
core_client = None


@mcp.on_startup
async def startup():
    """Initialize clients on server startup."""
    global settings, serpapi_client, core_client

    settings = get_settings()

    # SerpAPI client (required)
    serpapi_client = SerpAPIClient(api_key=settings.serpapi_api_key)

    # CORE API client (optional, for full-text access)
    if settings.core_api_key:
        core_client = CoreAPIClient(api_key=settings.core_api_key)
    else:
        core_client = CoreAPIClient()


@mcp.on_shutdown
async def shutdown():
    """Cleanup on server shutdown."""
    global serpapi_client, core_client

    if serpapi_client:
        await serpapi_client.close()
    if core_client:
        await core_client.close()


def get_serpapi_client() -> SerpAPIClient:
    """Get SerpAPI client instance."""
    if serpapi_client is None:
        raise RuntimeError("Server not initialized. SerpAPI client unavailable.")
    return serpapi_client


def get_core_client() -> CoreAPIClient:
    """Get CORE API client instance."""
    if core_client is None:
        raise RuntimeError("Server not initialized. CORE API client unavailable.")
    return core_client


# Register all tools
register_scholar_tools(mcp, get_serpapi_client)
register_fulltext_tools(mcp, get_core_client)


def main():
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
