# Google Scholar MCP Server

Private MCP server for searching Google Scholar using SerpAPI.

## Features

- Search academic articles
- Search author profiles  
- Get citation information
- Get article versions

## Prerequisites

- Docker Desktop 4.42+
- SerpAPI key (get at https://serpapi.com/)
- Claude Desktop

## Setup

1. Clone repository
2. Create `.env` file with your SerpAPI key:
   ```
   SERPAPI_API_KEY=your_key_here
   ```

3. Build Docker image:
   ```bash
   docker-compose build
   ```

## Configure Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "google-scholar": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--env-file",
        "/Users/alimov/mcp-servers/google-schoolar-mcp/.env",
        "google-scholar-mcp:latest"
      ]
    }
  }
}
```

## Available Tools

### search_articles
Search for academic articles on Google Scholar.

Parameters:
- `query` (required): Search query
- `year_from`: Filter from year
- `year_to`: Filter to year  
- `language`: Language code (default: "en")
- `num_results`: Number of results (max 20, default: 10)

### search_author
Search for author profiles.

Parameters:
- `author_name` (required): Author name to search

### get_citations
Get articles citing a specific paper.

Parameters:
- `citation_id` (required): Citation ID from search results
- `num_results`: Number of results (default: 10)

### get_article_versions
Get all versions of an article.

Parameters:
- `cluster_id` (required): Cluster ID from search results

## Usage Example

In Claude Desktop:
```
Search for recent machine learning papers from 2023
```

Claude will use the `search_articles` tool with appropriate parameters.

## Security

- API key stored in `.env` file (not in repository)
- Docker container runs as non-root user
- Isolated environment with minimal permissions