FROM python:3.12-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies into the system python
ENV UV_PROJECT_ENVIRONMENT="/usr/local"
RUN uv sync --frozen --no-dev

# Copy the rest of the application
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Run the application
CMD ["uv", "run", "streamlit", "run", "app/main.py", "--server.address=0.0.0.0"]
