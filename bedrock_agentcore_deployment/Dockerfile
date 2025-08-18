# Strands Personal AI Agent - Bedrock AgentCore Custom Agent
# Multi-stage build for optimized container size

FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code and all Strands agent files
COPY . .
COPY ../enhanced_context_aware_agent_strands.py .
COPY ../basic_agent_strands.py .
COPY ../weather_tool.py .
COPY ../bible_verse_tool.py .
COPY ../x_posting_tool.py .
COPY ../google_calendar_tool.py .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash --user-group appuser

# Change ownership of app directory
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Run the application
CMD ["python", "app.py"]