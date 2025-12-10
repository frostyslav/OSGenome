#!/bin/bash

# Docker build script for OSGenome with multi-stage optimization
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
IMAGE_NAME="osgenome"
TAG="latest"
TARGET="production"
DOCKERFILE="Dockerfile"
PUSH=false
CACHE=true
PLATFORM=""

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Build OSGenome Docker image with multi-stage optimization

OPTIONS:
    -n, --name NAME         Image name (default: osgenome)
    -t, --tag TAG          Image tag (default: latest)
    --target TARGET        Build target: production, development (default: production)
    -f, --file FILE        Dockerfile to use (default: auto-detected based on target)
    -p, --push             Push image to registry after build
    --no-cache             Build without using cache
    --platform PLATFORM   Target platform (e.g., linux/amd64,linux/arm64)
    -h, --help             Show this help message

EXAMPLES:
    $0                                    # Build production image
    $0 --target development               # Build development image
    $0 --name myregistry/osgenome --push  # Build and push to registry
    $0 --platform linux/amd64,linux/arm64 # Multi-platform build

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        --target)
            TARGET="$2"
            shift 2
            ;;
        -f|--file)
            DOCKERFILE="$2"
            shift 2
            ;;
        -p|--push)
            PUSH=true
            shift
            ;;
        --no-cache)
            CACHE=false
            shift
            ;;
        --platform)
            PLATFORM="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate target and set default Dockerfile
if [[ "$TARGET" == "production" ]]; then
    if [[ "$DOCKERFILE" == "Dockerfile" ]]; then
        DOCKERFILE="Dockerfile"
    fi
elif [[ "$TARGET" == "development" ]]; then
    if [[ "$DOCKERFILE" == "Dockerfile" ]]; then
        DOCKERFILE="Dockerfile.dev"
    fi
else
    print_error "Invalid target: $TARGET. Must be 'production' or 'development'"
    exit 1
fi

# Build Docker image
print_status "Building Docker image: ${IMAGE_NAME}:${TAG}"
print_status "Target: $TARGET"

# Prepare build command
BUILD_CMD="docker build"

# Add platform if specified
if [[ -n "$PLATFORM" ]]; then
    BUILD_CMD="$BUILD_CMD --platform $PLATFORM"
fi

# Add cache option
if [[ "$CACHE" == "false" ]]; then
    BUILD_CMD="$BUILD_CMD --no-cache"
fi

# Add dockerfile and tags
BUILD_CMD="$BUILD_CMD -f $DOCKERFILE -t ${IMAGE_NAME}:${TAG}"

# Add target for multi-stage builds (only for production Dockerfile)
if [[ "$DOCKERFILE" == "Dockerfile" ]]; then
    BUILD_CMD="$BUILD_CMD --target $TARGET"
fi

# Add build context
BUILD_CMD="$BUILD_CMD ."

print_status "Running: $BUILD_CMD"

# Execute build
if eval $BUILD_CMD; then
    print_success "Docker image built successfully: ${IMAGE_NAME}:${TAG}"
else
    print_error "Docker build failed"
    exit 1
fi

# Show image size
print_status "Image size:"
docker images "${IMAGE_NAME}:${TAG}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

# Push if requested
if [[ "$PUSH" == "true" ]]; then
    print_status "Pushing image to registry..."
    if docker push "${IMAGE_NAME}:${TAG}"; then
        print_success "Image pushed successfully: ${IMAGE_NAME}:${TAG}"
    else
        print_error "Failed to push image"
        exit 1
    fi
fi

# Show build summary
echo
print_success "Build Summary:"
echo "  Image: ${IMAGE_NAME}:${TAG}"
echo "  Dockerfile: $DOCKERFILE"
echo "  Target: $TARGET"
echo "  Platform: ${PLATFORM:-default}"
echo "  Cache: $CACHE"
echo "  Pushed: $PUSH"

# Show next steps
echo
print_status "Next steps:"
if [[ "$TARGET" == "production" ]]; then
    echo "  Run container: docker run -p 8080:8080 ${IMAGE_NAME}:${TAG}"
    echo "  Or use compose: docker-compose up"
else
    echo "  Run dev container: docker run -p 5000:5000 ${IMAGE_NAME}:${TAG}"
    echo "  Or use compose: docker-compose -f docker-compose.yml -f docker-compose.override.yml up"
fi
echo "  Health check: curl http://localhost:8080/api/health"