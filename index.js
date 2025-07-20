#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema
} from '@modelcontextprotocol/sdk/types.js';
import { GoogleSearch } from 'google-search-results-nodejs';
import dotenv from 'dotenv';

// Temporarily suppress console output from dotenv
const originalLog = console.log;
const originalError = console.error;
const originalWarn = console.warn;
console.log = () => {};
console.error = () => {};
console.warn = () => {};

// Load environment variables
dotenv.config();

// Restore console methods
console.log = originalLog;
console.error = originalError;
console.warn = originalWarn;

// Initialize Google Search client
const search = new GoogleSearch(process.env.SERPAPI_API_KEY);

// Define available tools
const TOOLS = [
  {
    name: 'search_articles',
    description: 'Search for academic articles on Google Scholar',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query for articles'
        },
        year_from: {
          type: 'number',
          description: 'Filter articles from this year (optional)'
        },
        year_to: {
          type: 'number',
          description: 'Filter articles up to this year (optional)'
        },
        language: {
          type: 'string',
          description: 'Language code (e.g., "en", "ru") (optional)',
          default: 'en'
        },
        num_results: {
          type: 'number',
          description: 'Number of results to return (max 20)',
          default: 10,
          minimum: 1,
          maximum: 20
        }
      },
      required: ['query']
    }
  },
  {
    name: 'search_author',
    description: 'Search for author profiles on Google Scholar',
    inputSchema: {
      type: 'object',
      properties: {
        author_name: {
          type: 'string',
          description: 'Name of the author to search'
        }
      },
      required: ['author_name']
    }
  },
  {
    name: 'get_citations',
    description: 'Get articles that cite a specific paper',
    inputSchema: {
      type: 'object',
      properties: {
        citation_id: {
          type: 'string',
          description: 'Citation ID from a previous search result'
        },
        num_results: {
          type: 'number',
          description: 'Number of citing articles to return',
          default: 10,
          minimum: 1,
          maximum: 20
        }
      },
      required: ['citation_id']
    }
  },
  {
    name: 'get_article_versions',
    description: 'Get all versions of a specific article',
    inputSchema: {
      type: 'object',
      properties: {
        cluster_id: {
          type: 'string',
          description: 'Cluster ID from a previous search result'
        }
      },
      required: ['cluster_id']
    }
  }
];

// Create MCP server
const server = new Server(
  {
    name: 'google-scholar-mcp',
    version: '1.0.0'
  },
  {
    capabilities: {
      tools: {}
    }
  }
);

// Handle tool listing
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: TOOLS
  };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  if (!process.env.SERPAPI_API_KEY) {
    throw new Error('SERPAPI_API_KEY environment variable is not set');
  }
  
  try {
    switch (name) {
      case 'search_articles': {
        const params = {
          engine: 'google_scholar',
          q: args.query,
          hl: args.language || 'en',
          num: args.num_results || 10
        };
        
        if (args.year_from) {
          params.as_ylo = args.year_from;
        }
        if (args.year_to) {
          params.as_yhi = args.year_to;
        }
        
        const result = await searchWithPromise(params);
        
        const articles = (result.organic_results || []).map(article => ({
          title: article.title,
          link: article.link,
          snippet: article.snippet,
          authors: article.publication_info?.authors?.map(a => a.name).join(', ') || 'Unknown',
          year: article.publication_info?.year || 'Unknown',
          citations: article.inline_links?.cited_by?.total || 0,
          citation_id: article.inline_links?.cited_by?.cites_id,
          cluster_id: article.inline_links?.cluster_id,
          pdf_link: article.resources?.find(r => r.file_format === 'PDF')?.link
        }));
        
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                query: args.query,
                total_results: articles.length,
                articles: articles
              }, null, 2)
            }
          ]
        };
      }
      
      case 'search_author': {
        const params = {
          engine: 'google_scholar_profiles',
          q: args.author_name
        };
        
        const result = await searchWithPromise(params);
        
        const profiles = (result.profiles || []).map(profile => ({
          name: profile.name,
          affiliations: profile.affiliations,
          email: profile.email,
          interests: profile.interests?.map(i => i.title).join(', ') || '',
          author_id: profile.author_id,
          citations: profile.cited_by?.all || 0
        }));
        
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                query: args.author_name,
                total_profiles: profiles.length,
                profiles: profiles
              }, null, 2)
            }
          ]
        };
      }
      
      case 'get_citations': {
        const params = {
          engine: 'google_scholar',
          cites: args.citation_id,
          num: args.num_results || 10
        };
        
        const result = await searchWithPromise(params);
        
        const citations = (result.organic_results || []).map(article => ({
          title: article.title,
          link: article.link,
          snippet: article.snippet,
          authors: article.publication_info?.authors?.map(a => a.name).join(', ') || 'Unknown',
          year: article.publication_info?.year || 'Unknown'
        }));
        
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                citation_id: args.citation_id,
                total_citations: citations.length,
                citing_articles: citations
              }, null, 2)
            }
          ]
        };
      }
      
      case 'get_article_versions': {
        const params = {
          engine: 'google_scholar',
          cluster: args.cluster_id
        };
        
        const result = await searchWithPromise(params);
        
        const versions = (result.organic_results || []).map(version => ({
          title: version.title,
          link: version.link,
          source: version.publication_info?.summary || 'Unknown',
          type: version.type || 'Unknown'
        }));
        
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                cluster_id: args.cluster_id,
                total_versions: versions.length,
                versions: versions
              }, null, 2)
            }
          ]
        };
      }
      
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`
        }
      ],
      isError: true
    };
  }
});

// Helper function to promisify search
function searchWithPromise(params) {
  return new Promise((resolve, reject) => {
    search.json(params, (result) => {
      if (result.error) {
        reject(new Error(result.error));
      } else {
        resolve(result);
      }
    });
  });
}

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Google Scholar MCP server started successfully');
}

main().catch((error) => {
  console.error('Failed to start server:', error);
  process.exit(1);
});