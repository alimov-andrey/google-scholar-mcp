FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install dependencies
RUN uv pip install --system --no-cache .

# Create non-root user
RUN addgroup --gid 1001 --system appuser && \
    adduser --system --uid 1001 --gid 1001 appuser

# Change ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# MCP servers communicate via stdio
ENTRYPOINT ["python", "-m", "src.main"]
