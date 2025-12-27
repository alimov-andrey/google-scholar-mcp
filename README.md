# Google Scholar MCP Server

MCP server for academic research via Claude Code. Search Google Scholar and access Open Access full-text articles.

## Features

- **Google Scholar Search** via SerpAPI
  - Search academic articles
  - Find author profiles
  - Get citing articles
  - Get article versions
- **Full-text Access** via CORE API
  - Retrieve full text of Open Access articles
  - Search specifically for articles with full-text available

## Tools

| Tool | Description |
|------|-------------|
| `search_articles` | Search for academic articles on Google Scholar |
| `search_author` | Search for author profiles |
| `get_citations` | Get articles citing a specific paper |
| `get_article_versions` | Get all versions of an article |
| `get_fulltext` | Get full text of Open Access article |
| `search_open_access` | Search for articles with full-text |

## Quick Start

### 1. Configure Environment

```bash
cp .env.example .env
# Add your SERPAPI_API_KEY
```

### 2. Build Docker Image

```bash
docker-compose build
```

### 3. Configure Claude Code

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "google-scholar": {
      "command": "docker",
      "args": ["run", "--rm", "-i", "--env-file", "/Users/alimov/mcp-servers/google-schoolar-mcp/.env", "google-scholar-mcp:latest"]
    }
  }
}
```

## API Keys

### SerpAPI (Required)
- Sign up at [serpapi.com](https://serpapi.com/)
- Free tier: 100 searches/month
- Paid plans from $75/month for 5,000 searches

### CORE API (Optional)
- Register at [core.ac.uk/api-keys/register](https://core.ac.uk/api-keys/register)
- Free: 100,000 requests/day
- Provides access to Open Access research papers

## Project Structure

```
google-scholar-mcp/
├── src/
│   ├── main.py              # FastMCP server
│   ├── config.py            # Settings
│   ├── clients/
│   │   ├── serpapi.py       # SerpAPI client
│   │   └── core_api.py      # CORE API client
│   ├── models/
│   │   └── scholar.py       # Pydantic models
│   └── tools/
│       ├── scholar.py       # Google Scholar tools
│       └── fulltext.py      # Full-text access tools
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

## License

MIT
