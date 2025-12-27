"""CORE API client for Open Access full-text access."""

from typing import Any, Optional

import httpx


class CoreAPIClient:
    """Async HTTP client for CORE API v3.

    CORE aggregates Open Access research outputs from repositories worldwide.
    Free API key available at: https://core.ac.uk/api-keys/register
    """

    BASE_URL = "https://api.core.ac.uk/v3"

    def __init__(self, api_key: Optional[str] = None, timeout: float = 30.0):
        """Initialize client.

        Args:
            api_key: Optional CORE API key (higher rate limits with key)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with optional auth."""
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def search_works(
        self,
        query: str,
        fulltext: bool = True,
        limit: int = 10,
        offset: int = 0,
    ) -> dict[str, Any]:
        """Search for works (articles, papers).

        Args:
            query: Search query (supports field:value syntax)
            fulltext: Only return works with full-text available
            limit: Maximum results (max 100)
            offset: Pagination offset

        Returns:
            Search results with 'results' array
        """
        params = {
            "q": query,
            "limit": min(limit, 100),
            "offset": offset,
        }
        if fulltext:
            params["fulltext"] = "true"

        response = await self._client.get(
            f"{self.BASE_URL}/search/works",
            params=params,
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()

    async def get_work(self, work_id: str) -> dict[str, Any]:
        """Get a specific work by CORE ID.

        Args:
            work_id: CORE work ID

        Returns:
            Work details including fullText if available
        """
        response = await self._client.get(
            f"{self.BASE_URL}/works/{work_id}",
            headers=self._get_headers(),
        )
        response.raise_for_status()
        return response.json()

    async def search_by_doi(self, doi: str) -> Optional[dict[str, Any]]:
        """Search for a work by DOI.

        Args:
            doi: Digital Object Identifier

        Returns:
            Work details or None if not found
        """
        result = await self.search_works(f"doi:{doi}", fulltext=False, limit=1)
        results = result.get("results", [])
        return results[0] if results else None

    async def search_by_title(self, title: str) -> Optional[dict[str, Any]]:
        """Search for a work by title.

        Args:
            title: Article title

        Returns:
            Best matching work or None
        """
        result = await self.search_works(f"title:{title}", fulltext=True, limit=1)
        results = result.get("results", [])
        return results[0] if results else None

    async def get_fulltext(self, work_id: str) -> Optional[str]:
        """Get full text of a work.

        Args:
            work_id: CORE work ID

        Returns:
            Full text string or None
        """
        work = await self.get_work(work_id)
        return work.get("fullText")

    async def get_download_url(self, work_id: str) -> Optional[str]:
        """Get download URL for a work.

        Args:
            work_id: CORE work ID

        Returns:
            Download URL or None
        """
        work = await self.get_work(work_id)
        return work.get("downloadUrl")
