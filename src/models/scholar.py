"""Pydantic models for Google Scholar data."""

from typing import Optional

from pydantic import BaseModel, Field


# --- Article Models ---


class Article(BaseModel):
    """Academic article from Google Scholar."""

    title: str
    link: Optional[str] = None
    snippet: Optional[str] = None
    authors: str = "Unknown"
    year: Optional[str] = None
    citations: int = 0
    citation_id: Optional[str] = Field(
        default=None,
        description="ID for fetching citing articles",
    )
    cluster_id: Optional[str] = Field(
        default=None,
        description="ID for fetching article versions",
    )
    pdf_link: Optional[str] = None


class SearchArticlesResult(BaseModel):
    """Result of article search."""

    query: str
    total_results: int
    articles: list[Article]


# --- Citation Models ---


class CitingArticle(BaseModel):
    """Article that cites another article."""

    title: str
    link: Optional[str] = None
    snippet: Optional[str] = None
    authors: str = "Unknown"
    year: Optional[str] = None


class CitationsResult(BaseModel):
    """Result of citations lookup."""

    citation_id: str
    total_citations: int
    citing_articles: list[CitingArticle]


# --- Version Models ---


class ArticleVersion(BaseModel):
    """Version of an article from different sources."""

    title: str
    link: Optional[str] = None
    source: str = "Unknown"
    type: str = "Unknown"


class VersionsResult(BaseModel):
    """Result of article versions lookup."""

    cluster_id: str
    total_versions: int
    versions: list[ArticleVersion]


# --- Fulltext Models ---


class FulltextResult(BaseModel):
    """Result of full-text lookup."""

    title: Optional[str] = None
    abstract: Optional[str] = None
    download_url: Optional[str] = None
    fulltext_available: bool = False
    fulltext: Optional[str] = None
    source: str = "CORE API"


class OpenAccessArticle(BaseModel):
    """Open Access article with full-text availability."""

    title: str
    authors: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    download_url: Optional[str] = None
    abstract: Optional[str] = None
    core_id: Optional[str] = None


class SearchOpenAccessResult(BaseModel):
    """Result of Open Access search."""

    query: str
    total_results: int
    articles: list[OpenAccessArticle]


