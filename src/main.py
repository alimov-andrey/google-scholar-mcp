"""Google Scholar MCP Server - Entry Point."""

from contextlib import asynccontextmanager

from fastmcp import FastMCP

from .config import get_settings
from .clients.serpapi import SerpAPIClient
from .clients.core_api import CoreAPIClient
from .tools.scholar import register_scholar_tools
from .tools.fulltext import register_fulltext_tools

# Global client references (set during lifespan)
_serpapi_client: SerpAPIClient | None = None
_core_client: CoreAPIClient | None = None


@asynccontextmanager
async def lifespan(server: FastMCP):
    """Server lifespan - initialize and cleanup clients."""
    global _serpapi_client, _core_client

    # Startup
    settings = get_settings()

    # SerpAPI client (required)
    _serpapi_client = SerpAPIClient(api_key=settings.serpapi_api_key)

    # CORE API client (optional, for full-text access)
    if settings.core_api_key:
        _core_client = CoreAPIClient(api_key=settings.core_api_key)
    else:
        _core_client = CoreAPIClient()

    yield

    # Shutdown
    if _serpapi_client:
        await _serpapi_client.close()
    if _core_client:
        await _core_client.close()


def get_serpapi_client() -> SerpAPIClient:
    """Get SerpAPI client instance."""
    if _serpapi_client is None:
        raise RuntimeError("Server not initialized. SerpAPI client unavailable.")
    return _serpapi_client


def get_core_client() -> CoreAPIClient:
    """Get CORE API client instance."""
    if _core_client is None:
        raise RuntimeError("Server not initialized. CORE API client unavailable.")
    return _core_client


# Initialize FastMCP server with lifespan
mcp = FastMCP(
    name="google-scholar-mcp",
    version="2.0.0",
    lifespan=lifespan,
)

# Register all tools
register_scholar_tools(mcp, get_serpapi_client)
register_fulltext_tools(mcp, get_core_client)


def main():
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
