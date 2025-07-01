# Dockerfile
FROM python:3.11-slim

# Accept version as build argument
ARG VERSION=latest

# Set metadata
LABEL maintainer="Rolfe Dlugy-Hegwer <rolfedh@users.noreply.github.com>"
LABEL description="AsciiDoc DITA Toolkit - CLI tools for processing AsciiDoc files for DITA publishing workflows"
LABEL version=$VERSION

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 toolkit

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy the source code
COPY asciidoc_dita_toolkit/ ./asciidoc_dita_toolkit/
COPY pyproject.toml README.md LICENSE ./

# Copy beta testing files for user convenience
COPY beta-testing/ ./beta-testing/
COPY docs/ ./docs/

# Install the package in development mode
RUN pip install -e .

# Switch to non-root user
USER toolkit

# Set the default working directory for mounted volumes
WORKDIR /workspace

# Default command
ENTRYPOINT ["asciidoc-dita-toolkit"]
CMD ["--help"]
