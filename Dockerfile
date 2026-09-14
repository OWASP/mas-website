# Use the latest Python image
FROM python:3.12-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y git jq curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Set the working directory this way to be compatible with devcontainers and also run independently
WORKDIR /workspaces/mas-website

# Expose port 8000
EXPOSE 8000

# Start the container with a shell
# Rely on MkDocs hooks to watch external repos; just serve
CMD ["sh", "-c", "mkdocs serve -a 0.0.0.0:8000"]
