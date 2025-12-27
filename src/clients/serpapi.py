"""SerpAPI client for Google Scholar access."""

from typing import Any

import httpx


class SerpAPIClient:
    """Async HTTP client for SerpAPI Google Scholar endpoints."""

    BASE_URL = "https://serpapi.com/search"

    def __init__(self, api_key: str, timeout: float = 30.0):
        """Initialize client with API key.

        Args:
            api_key: SerpAPI API key
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def _request(self, params: dict[str, Any]) -> dict[str, Any]:
        """Make request to SerpAPI.

        Args:
            params: Query parameters

        Returns:
            JSON response

        Raises:
            httpx.HTTPStatusError: On HTTP errors
            ValueError: On API errors
        """
        params["api_key"] = self.api_key
        response = await self._client.get(self.BASE_URL, params=params)
        response.raise_for_status()

        data = response.json()
        if "error" in data:
            raise ValueError(f"SerpAPI error: {data['error']}")

        return data

    async def search_scholar(
        self,
        query: str,
        language: str = "en",
        num_results: int = 10,
        year_from: int | None = None,
        year_to: int | None = None,
    ) -> dict[str, Any]:
        """Search Google Scholar for articles.

        Args:
            query: Search query
            language: Language code (e.g., 'en', 'ru')
            num_results: Number of results (max 20)
            year_from: Filter from year
            year_to: Filter to year

        Returns:
            Search results with organic_results
        """
        params = {
            "engine": "google_scholar",
            "q": query,
            "hl": language,
            "num": min(num_results, 20),
        }
        if year_from:
            params["as_ylo"] = year_from
        if year_to:
            params["as_yhi"] = year_to

        return await self._request(params)

    async def search_profiles(self, author_name: str) -> dict[str, Any]:
        """Search Google Scholar for author profiles.

        Args:
            author_name: Name of the author

        Returns:
            Search results with profiles
        """
        params = {
            "engine": "google_scholar_profiles",
            "q": author_name,
        }
        return await self._request(params)

    async def get_citations(
        self,
        citation_id: str,
        num_results: int = 10,
    ) -> dict[str, Any]:
        """Get articles citing a specific paper.

        Args:
            citation_id: Citation ID from previous search
            num_results: Number of results (max 20)

        Returns:
            Search results with citing articles
        """
        params = {
            "engine": "google_scholar",
            "cites": citation_id,
            "num": min(num_results, 20),
        }
        return await self._request(params)

    async def get_cluster(self, cluster_id: str) -> dict[str, Any]:
        """Get all versions of an article by cluster ID.

        Args:
            cluster_id: Cluster ID from previous search

        Returns:
            Search results with article versions
        """
        params = {
            "engine": "google_scholar",
            "cluster": cluster_id,
        }
        return await self._request(params)
