"""Google Scholar tools - migrated from Node.js implementation."""

from typing import Callable, Optional

from fastmcp import FastMCP
from pydantic import Field

from ..clients.serpapi import SerpAPIClient
from ..models.scholar import (
    Article,
    Author,
    ArticleVersion,
    CitingArticle,
    CitationsResult,
    SearchArticlesResult,
    SearchAuthorResult,
    VersionsResult,
)


def register_scholar_tools(
    mcp: FastMCP,
    get_client: Callable[[], SerpAPIClient],
):
    """Register Google Scholar tools with MCP server.

    Args:
        mcp: FastMCP server instance
        get_client: Function to get SerpAPI client
    """

    @mcp.tool()
    async def search_articles(
        query: str = Field(..., description="Search query for articles"),
        year_from: Optional[int] = Field(None, description="Filter articles from this year"),
        year_to: Optional[int] = Field(None, description="Filter articles up to this year"),
        language: str = Field("en", description="Language code (e.g., 'en', 'ru')"),
        num_results: int = Field(10, ge=1, le=20, description="Number of results (max 20)"),
    ) -> SearchArticlesResult:
        """Search for academic articles on Google Scholar.

        Returns articles with title, authors, year, citation count, and links.
        Use citation_id for get_citations and cluster_id for get_article_versions.
        """
        client = get_client()

        result = await client.search_scholar(
            query=query,
            language=language,
            num_results=num_results,
            year_from=year_from,
            year_to=year_to,
        )

        articles = []
        for item in result.get("organic_results", []):
            # Extract authors
            pub_info = item.get("publication_info", {})
            authors_list = pub_info.get("authors", [])
            authors = ", ".join(a.get("name", "") for a in authors_list) if authors_list else "Unknown"

            # Extract citation info
            inline_links = item.get("inline_links", {})
            cited_by = inline_links.get("cited_by", {})

            # Extract PDF link
            resources = item.get("resources", [])
            pdf_link = next(
                (r.get("link") for r in resources if r.get("file_format") == "PDF"),
                None,
            )

            articles.append(
                Article(
                    title=item.get("title", ""),
                    link=item.get("link"),
                    snippet=item.get("snippet"),
                    authors=authors,
                    year=pub_info.get("year"),
                    citations=cited_by.get("total", 0),
                    citation_id=cited_by.get("cites_id"),
                    cluster_id=inline_links.get("cluster_id"),
                    pdf_link=pdf_link,
                )
            )

        return SearchArticlesResult(
            query=query,
            total_results=len(articles),
            articles=articles,
        )

    @mcp.tool()
    async def search_author(
        author_name: str = Field(..., description="Name of the author to search"),
    ) -> SearchAuthorResult:
        """Search for author profiles on Google Scholar.

        Returns author profiles with name, affiliations, interests, and citation count.
        """
        client = get_client()

        result = await client.search_profiles(author_name)

        profiles = []
        for profile in result.get("profiles", []):
            # Extract interests
            interests_list = profile.get("interests", [])
            interests = ", ".join(i.get("title", "") for i in interests_list) if interests_list else ""

            profiles.append(
                Author(
                    name=profile.get("name", ""),
                    affiliations=profile.get("affiliations"),
                    email=profile.get("email"),
                    interests=interests,
                    author_id=profile.get("author_id"),
                    citations=profile.get("cited_by", {}).get("all", 0),
                )
            )

        return SearchAuthorResult(
            query=author_name,
            total_profiles=len(profiles),
            profiles=profiles,
        )

    @mcp.tool()
    async def get_citations(
        citation_id: str = Field(..., description="Citation ID from a previous search result"),
        num_results: int = Field(10, ge=1, le=20, description="Number of citing articles (max 20)"),
    ) -> CitationsResult:
        """Get articles that cite a specific paper.

        Use the citation_id from search_articles results.
        """
        client = get_client()

        result = await client.get_citations(citation_id, num_results)

        citing_articles = []
        for item in result.get("organic_results", []):
            pub_info = item.get("publication_info", {})
            authors_list = pub_info.get("authors", [])
            authors = ", ".join(a.get("name", "") for a in authors_list) if authors_list else "Unknown"

            citing_articles.append(
                CitingArticle(
                    title=item.get("title", ""),
                    link=item.get("link"),
                    snippet=item.get("snippet"),
                    authors=authors,
                    year=pub_info.get("year"),
                )
            )

        return CitationsResult(
            citation_id=citation_id,
            total_citations=len(citing_articles),
            citing_articles=citing_articles,
        )

    @mcp.tool()
    async def get_article_versions(
        cluster_id: str = Field(..., description="Cluster ID from a previous search result"),
    ) -> VersionsResult:
        """Get all versions of a specific article from different sources.

        Use the cluster_id from search_articles results.
        """
        client = get_client()

        result = await client.get_cluster(cluster_id)

        versions = []
        for item in result.get("organic_results", []):
            pub_info = item.get("publication_info", {})

            versions.append(
                ArticleVersion(
                    title=item.get("title", ""),
                    link=item.get("link"),
                    source=pub_info.get("summary", "Unknown"),
                    type=item.get("type", "Unknown"),
                )
            )

        return VersionsResult(
            cluster_id=cluster_id,
            total_versions=len(versions),
            versions=versions,
        )
