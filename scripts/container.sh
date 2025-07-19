#!/bin/bash
# Container helper script for asciidoc-dita-toolkit

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="asciidoc-dita-toolkit"
REGISTRY="rolfedh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get version from pyproject.toml
get_version() {
    grep '^version = ' "$PROJECT_ROOT/pyproject.toml" | sed 's/version = "\(.*\)"/\1/'
}

show_help() {
    cat << EOF
Container Helper Script for AsciiDoc DITA Toolkit

Usage: $0 [COMMAND] [OPTIONS]

Commands:
  build [--prod]     Build container image(s)
  run [ARGS...]      Run the toolkit in container
  shell              Start interactive shell in container
  test               Run tests in container
  push [--prod]      Push image(s) to registry
  clean              Remove local container images
  help               Show this help message

Examples:
  $0 build                    # Build development container
  $0 build --prod            # Build production container
  $0 run ContentType docs/   # Run ContentType plugin on docs/
  $0 shell                   # Start interactive shell
  $0 test                    # Run test suite
  $0 push                    # Push to GitHub Container Registry (ghcr.io)
  $0 clean                   # Clean up local images

EOF
}

build_container() {
    local prod_mode=false
    local dockerfile="Dockerfile"
    local tag_suffix=""
    
    if [[ "$1" == "--prod" ]]; then
        prod_mode=true
        dockerfile="Dockerfile.production"
        tag_suffix="-prod"
    fi
    
    local version=$(get_version)
    local full_tag="$REGISTRY/$IMAGE_NAME$tag_suffix"
    
    log_info "Building container image: $full_tag:$version"
    log_info "Using Dockerfile: $dockerfile"
    
    cd "$PROJECT_ROOT"
    
    if [[ "$prod_mode" == true ]]; then
        # Use VERSION build arg for production builds
        docker build -f "$dockerfile" --build-arg VERSION="$version" -t "$full_tag:latest" -t "$full_tag:$version" .
    else
        docker build -f "$dockerfile" -t "$full_tag:latest" -t "$full_tag:$version" .
    fi
    
    log_info "Container built successfully!"
    log_info "Tags: $full_tag:latest, $full_tag:$version"
}

run_container() {
    local version=$(get_version)
    local full_tag="$REGISTRY/$IMAGE_NAME:$version"
    
    # Check if image exists
    if ! docker image inspect "$full_tag" &> /dev/null; then
        log_warn "Image $full_tag not found. Building it now..."
        build_container
    fi
    
    log_info "Running: $full_tag $*"
    docker run --rm -v "$PROJECT_ROOT:/workspace" "$full_tag" "$@"
}

start_shell() {
    local version=$(get_version)
    local full_tag="$REGISTRY/$IMAGE_NAME:$version"
    
    # Check if image exists
    if ! docker image inspect "$full_tag" &> /dev/null; then
        log_warn "Image $full_tag not found. Building it now..."
        build_container
    fi
    
    log_info "Starting interactive shell in: $full_tag"
    docker run --rm -it -v "$PROJECT_ROOT:/workspace" "$full_tag" /bin/bash
}

run_tests() {
    log_info "Running tests in container..."
    cd "$PROJECT_ROOT"
    docker-compose run --rm test
}

push_container() {
    local prod_mode=false
    local tag_suffix=""
    
    if [[ "$1" == "--prod" ]]; then
        prod_mode=true
        tag_suffix="-prod"
    fi
    
    local version=$(get_version)
    local full_tag="$REGISTRY/$IMAGE_NAME$tag_suffix"
    
    # Check if images exist locally before pushing
    if ! docker image inspect "$full_tag:latest" &> /dev/null; then
        log_error "Image $full_tag:latest not found locally. Please run: $0 build${1:+ $1}"
        exit 1
    fi
    
    if ! docker image inspect "$full_tag:$version" &> /dev/null; then
        log_error "Image $full_tag:$version not found locally. Please run: $0 build${1:+ $1}"
        exit 1
    fi
    
    log_info "Pushing container image: $full_tag"

    if ! docker push "$full_tag:latest"; then
        log_error "Failed to push $full_tag:latest. Are you logged in to GitHub Container Registry? Please check your GitHub authentication."
        exit 1
    fi

    if ! docker push "$full_tag:$version"; then
        log_error "Failed to push $full_tag:$version. Are you logged in to GitHub Container Registry? Please check your GitHub authentication."
        exit 1
    fi

    log_info "Container pushed successfully!"
    log_info "Images available at:"
    log_info "  - $full_tag:latest"
    log_info "  - $full_tag:$version"
}

clean_containers() {
    local version=$(get_version)
    
    log_info "Cleaning up local container images..."
    
    # Remove development images
    docker rmi "$REGISTRY/$IMAGE_NAME:latest" 2>/dev/null || true
    docker rmi "$REGISTRY/$IMAGE_NAME:$version" 2>/dev/null || true
    
    # Remove production images
    docker rmi "$REGISTRY/$IMAGE_NAME-prod:latest" 2>/dev/null || true
    docker rmi "$REGISTRY/$IMAGE_NAME-prod:$version" 2>/dev/null || true
    
    # Clean up dangling images
    docker image prune -f
    
    log_info "Cleanup completed!"
}

# Main command handling
case "${1:-}" in
    build)
        build_container "$2"
        ;;
    run)
        shift
        run_container "$@"
        ;;
    shell)
        start_shell
        ;;
    test)
        run_tests
        ;;
    push)
        push_container "$2"
        ;;
    clean)
        clean_containers
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        log_error "No command specified. Use '$0 help' for usage information."
        exit 1
        ;;
    *)
        log_error "Unknown command: $1"
        log_error "Use '$0 help' for usage information."
        exit 1
        ;;
esac
