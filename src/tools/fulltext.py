"""Full-text access tools using CORE API."""

from typing import Callable, Optional

from fastmcp import FastMCP
from pydantic import Field

from ..clients.core_api import CoreAPIClient
from ..models.scholar import (
    FulltextResult,
    OpenAccessArticle,
    SearchOpenAccessResult,
)


def register_fulltext_tools(
    mcp: FastMCP,
    get_client: Callable[[], CoreAPIClient],
):
    """Register full-text access tools with MCP server.

    Args:
        mcp: FastMCP server instance
        get_client: Function to get CORE API client
    """

    @mcp.tool()
    async def get_fulltext(
        doi: Optional[str] = Field(None, description="DOI of the article"),
        title: Optional[str] = Field(None, description="Title of the article"),
        core_id: Optional[str] = Field(None, description="CORE ID of the article"),
    ) -> FulltextResult:
        """Get full text of an Open Access article via CORE API.

        Provide at least one identifier: DOI, title, or CORE ID.
        Returns full text if available, otherwise abstract and download link.
        """
        if not any([doi, title, core_id]):
            raise ValueError("Provide at least one of: doi, title, or core_id")

        client = get_client()
        work = None

        # Try to find the work
        if core_id:
            try:
                work = await client.get_work(core_id)
            except Exception:
                pass

        if not work and doi:
            work = await client.search_by_doi(doi)

        if not work and title:
            work = await client.search_by_title(title)

        if not work:
            return FulltextResult(
                title=title,
                fulltext_available=False,
                source="CORE API",
            )

        return FulltextResult(
            title=work.get("title"),
            abstract=work.get("abstract"),
            download_url=work.get("downloadUrl"),
            fulltext_available=work.get("fullText") is not None,
            fulltext=work.get("fullText"),
            source="CORE API",
        )

    @mcp.tool()
    async def search_open_access(
        query: str = Field(..., description="Search query for Open Access articles"),
        limit: int = Field(10, ge=1, le=50, description="Number of results (max 50)"),
    ) -> SearchOpenAccessResult:
        """Search for Open Access articles with full-text available.

        Returns articles from CORE aggregator with direct download links.
        """
        client = get_client()

        result = await client.search_works(query=query, fulltext=True, limit=limit)

        articles = []
        for item in result.get("results", []):
            # Extract authors
            authors_list = item.get("authors", [])
            if authors_list:
                authors = ", ".join(
                    a.get("name", "") if isinstance(a, dict) else str(a)
                    for a in authors_list
                )
            else:
                authors = None

            articles.append(
                OpenAccessArticle(
                    title=item.get("title", ""),
                    authors=authors,
                    year=item.get("yearPublished"),
                    doi=item.get("doi"),
                    download_url=item.get("downloadUrl"),
                    abstract=item.get("abstract"),
                    core_id=str(item.get("id")) if item.get("id") else None,
                )
            )

        return SearchOpenAccessResult(
            query=query,
            total_results=len(articles),
            articles=articles,
        )
