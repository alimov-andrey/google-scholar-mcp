FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
# Use additional flags to suppress all npm output
RUN npm ci --only=production --silent --no-progress --no-audit --no-fund 2>/dev/null || npm ci --only=production

# Copy application files
COPY index.js ./

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Change ownership
RUN chown -R nodejs:nodejs /app

# Switch to non-root user
USER nodejs

# Disable dotenv output
ENV DOTENV_CONFIG_SILENT=true

# MCP servers communicate via stdio
ENTRYPOINT ["node", "index.js"]