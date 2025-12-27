# Google Scholar MCP Server

MCP server for academic research via Claude Code. Search Google Scholar and access Open Access full-text articles.

## Features

- **Google Scholar Search** via SerpAPI
  - Search academic articles by query, year, language
  - Get articles citing a specific paper
  - Get all versions of an article from different sources
- **Full-text Access** via CORE API
  - Retrieve full text of Open Access articles
  - Search specifically for articles with full-text available

## Tools

| Tool | Description |
|------|-------------|
| `search_articles` | Search for academic articles on Google Scholar |
| `get_citations` | Get articles citing a specific paper |
| `get_article_versions` | Get all versions of an article |
| `get_fulltext` | Get full text of Open Access article |
| `search_open_access` | Search for articles with full-text |

## Quick Start

### 1. Get API Keys

**SerpAPI (Required)**
- Sign up at [serpapi.com](https://serpapi.com/)
- Free tier: 100 searches/month
- Paid plans from $75/month for 5,000 searches

**CORE API (Optional, for full-text)**
- Register at [core.ac.uk/api-keys/register](https://core.ac.uk/api-keys/register)
- Free: 100,000 requests/day

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys:
# SERPAPI_API_KEY=your_key_here
# CORE_API_KEY=your_key_here  # optional
```

### 3. Build Docker Image

```bash
docker compose build
```

### 4. Configure Claude Code

**Option A: Global config** (`~/.claude.json`)

```json
{
  "mcpServers": {
    "google-scholar": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--env-file", "/path/to/your/.env", "google-scholar-mcp:latest"]
    }
  }
}
```

**Option B: Project config** (`.mcp.json` in project root)

```json
{
  "mcpServers": {
    "google-scholar": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--env-file", "/path/to/your/.env", "google-scholar-mcp:latest"]
    }
  }
}
```

## Usage Examples

### Search Articles
```
Search for "transformer neural networks" articles from 2023
```

### Get Citations
```
Get articles citing this paper (use citation_id from search results)
```

### Get Full Text
```
Get full text for article with DOI 10.1234/example
```

## Project Structure

```
google-scholar-mcp/
├── src/
│   ├── main.py              # FastMCP server entry point
│   ├── config.py            # Pydantic settings
│   ├── clients/
│   │   ├── serpapi.py       # SerpAPI async client
│   │   └── core_api.py      # CORE API async client
│   ├── models/
│   │   └── scholar.py       # Pydantic response models
│   └── tools/
│       ├── scholar.py       # Google Scholar tools
│       └── fulltext.py      # Full-text access tools
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/
    └── test.yml             # CI/CD pipeline
```

## Development

```bash
# Install dependencies
uv pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Check syntax
python -m py_compile src/main.py
```

## Tech Stack

- **Python 3.12** + **fastmcp 2.14.1**
- **httpx** for async HTTP
- **Pydantic** for data validation
- **Docker** for containerization

## License

MIT
