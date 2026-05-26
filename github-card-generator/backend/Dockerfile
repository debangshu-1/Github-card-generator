FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock requirements.txt ./

# Install dependencies
RUN uv pip install --no-cache -r requirements.txt

# Copy source code
COPY . .

# Set environment variables
ENV PORT=8080
ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 8080

# Run with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
