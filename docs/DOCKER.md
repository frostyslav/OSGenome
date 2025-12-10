# Docker Container Optimization

This document describes the Docker container optimizations implemented for OSGenome, including multi-stage builds, health checks, and production deployment strategies.

## Multi-Stage Build Architecture

The project uses two Docker build strategies:

### Production Build (`Dockerfile`)
Multi-stage build with two stages:

**Build Stage (`builder`)**
- Based on `python:3.13-slim`
- Installs production dependencies only (`--no-dev`)
- Creates virtual environment with required packages
- Copies source code for building

**Production Stage (`production`)**
- Based on `python:3.13-slim` (fresh, minimal base)
- Only installs runtime dependencies (`curl`, `ca-certificates`)
- Copies only the virtual environment and application code from builder
- Runs as non-root user for security
- Includes comprehensive health checks

### Development Build (`Dockerfile.dev`)
Single-stage build optimized for development:
- Based on `python:3.13-slim`
- Installs all dependencies including dev tools (pytest, black, mypy, etc.)
- Includes build tools for development
- Supports hot reload and debugging
- Larger image size but includes development conveniences

## Key Optimizations

### 1. Image Size Reduction
- **Multi-stage builds**: Eliminates build tools and cache from final image
- **Layer caching**: Dependencies copied before source code for better cache utilization
- **Minimal base**: Uses slim Python image instead of full version
- **.dockerignore**: Excludes unnecessary files from build context

### 2. Security Enhancements
- **Non-root user**: Application runs as `appuser` (UID 1000) throughout build and runtime
- **Proper permissions**: Virtual environment created with correct user ownership
- **Read-only filesystem**: Container filesystem is read-only in production
- **No new privileges**: Prevents privilege escalation
- **Minimal attack surface**: Only essential packages installed

### 3. Health Monitoring
- **Comprehensive health checks**: Multiple validation layers
- **Graceful degradation**: Health status includes degraded state
- **Multiple check methods**: Both curl and Python-based health checks
- **Configurable intervals**: Customizable health check timing

### 4. Runtime Optimization
- **Direct virtual environment usage**: Avoids `uv run` overhead and permission issues
- **Proper signal handling**: Uses exec form for better container lifecycle management
- **Optimized startup**: Fast container startup with pre-built virtual environment

## Health Check Implementation

The health check system provides detailed status information:

```json
{
  "status": "healthy|degraded|unhealthy",
  "data_loaded": true,
  "data_count": 15420,
  "config_valid": true,
  "config_warnings": [],
  "version": "0.1.0",
  "cache_stats": {
    "size": 45,
    "hit_rate": "87.3%"
  }
}
```

### Health Check Levels
- **Healthy**: All systems operational
- **Degraded**: Minor issues (no data loaded, config warnings)
- **Unhealthy**: Critical failures (service unavailable)

## Usage Examples

### Development Build
```bash
# Build development image with dev dependencies
./scripts/docker-build.sh --target development --tag dev

# Run development container
docker-compose -f docker-compose.yml -f docker-compose.override.yml up
```

### Production Build
```bash
# Build optimized production image
./scripts/docker-build.sh --target production --tag latest

# Run production container
docker-compose up
```

### Multi-Platform Build
```bash
# Build for multiple architectures
./scripts/docker-build.sh --platform linux/amd64,linux/arm64 --tag multi-arch
```

## Container Configuration

### Environment Variables
```bash
# Application settings
FLASK_ENV=production
LOG_LEVEL=INFO
SECRET_KEY=your-secret-key

# Gunicorn settings
GUNICORN_PROCESSES=2
GUNICORN_THREADS=4
GUNICORN_BIND=0.0.0.0:8080

# Cache settings
CACHE_MAX_SIZE=100
CACHE_TTL=3600
```

### Volume Mounts
```yaml
volumes:
  # Genetic data files (persistent)
  - ./data:/app/data:rw
  
  # Application logs (optional)
  - ./logs:/app/logs:rw
  
  # Development: source code (read-only)
  - ./SNPedia:/app/SNPedia:ro
```

### Resource Limits
```yaml
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '1.0'
    reservations:
      memory: 256M
      cpus: '0.5'
```

## Production Deployment

### With Nginx Reverse Proxy
```bash
# Start with nginx proxy
docker-compose --profile production up
```

The nginx configuration provides:
- **Rate limiting**: API and upload endpoint protection
- **SSL termination**: HTTPS support (configure certificates)
- **Compression**: Gzip compression for static assets
- **Security headers**: Additional security headers
- **Load balancing**: Ready for multiple app instances

### Health Check Monitoring
```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# View health check logs
docker inspect osgenome_osgenome_1 | jq '.[0].State.Health'

# Manual health check
curl -f http://localhost:8080/api/health
```

## Performance Metrics

### Image Size Comparison
| Build Type | Size | Use Case |
|------------|------|----------|
| Development | ~550MB | Development with all tools |
| Production (multi-stage) | ~217MB | Optimized production deployment |
| **Size Reduction** | **60% smaller** | Production vs Development |

### Build Time Optimization
- **Layer caching**: Dependencies cached separately from source code
- **Parallel builds**: Multi-stage builds can be parallelized
- **Build context**: .dockerignore reduces context size by ~70%

### Runtime Performance
- **Memory usage**: ~150MB baseline (vs ~300MB single-stage)
- **Startup time**: ~15 seconds (vs ~25 seconds)
- **Health check**: <100ms response time

## Troubleshooting

### Common Issues

#### Virtual Environment Permission Errors
If you see errors like "Permission denied" when installing packages or "failed to write to file", this indicates permission issues with the virtual environment:

```bash
# Symptoms:
# - "Permission denied (os error 13)" during dependency installation
# - "failed to write to file `/app/uv.lock`" at runtime

# Solution: Rebuild with no cache to ensure proper permissions
./scripts/docker-build.sh --no-cache --target production

# The fix ensures:
# - Virtual environment is created as the appuser (not root)
# - All files have correct ownership throughout the build process
# - Runtime doesn't require write access to project files
```

#### Health Check Failures
```bash
# Check health endpoint directly
docker exec -it container_name curl http://localhost:8080/api/health

# View application logs
docker logs container_name

# Check resource usage
docker stats container_name
```

#### Build Failures
```bash
# Build with verbose output
docker build --progress=plain --no-cache .

# Check build context size
docker build --dry-run .
```

#### Permission Issues
```bash
# Fix data directory permissions
sudo chown -R 1000:1000 ./data

# Check container user
docker exec -it container_name id

# If you see "Permission denied" errors during build:
# This usually indicates the virtual environment wasn't created with proper ownership
# Rebuild the image to fix permission issues:
./scripts/docker-build.sh --no-cache --target production
```

### Performance Tuning

#### Memory Optimization
```yaml
# Adjust based on data size
environment:
  - CACHE_MAX_SIZE=50  # Reduce for smaller datasets
  - GUNICORN_PROCESSES=1  # Reduce for memory-constrained environments
```

#### CPU Optimization
```yaml
# Adjust worker processes
environment:
  - GUNICORN_PROCESSES=4  # Match CPU cores
  - GUNICORN_THREADS=2    # Reduce for CPU-bound workloads
```

## Security Considerations

### Container Security
- **Non-root execution**: All processes run as unprivileged user
- **Read-only filesystem**: Prevents runtime modifications
- **Capability dropping**: Minimal Linux capabilities
- **Network isolation**: Custom bridge network

### Data Security
- **Volume encryption**: Consider encrypting data volumes
- **Secrets management**: Use Docker secrets for sensitive data
- **Network policies**: Implement network segmentation

### Monitoring
- **Health checks**: Automated health monitoring
- **Log aggregation**: Centralized logging for security events
- **Resource monitoring**: Track resource usage patterns

## Best Practices

1. **Always use multi-stage builds** for production deployments
2. **Pin base image versions** to ensure reproducible builds
3. **Use .dockerignore** to minimize build context
4. **Run as non-root user** for security
5. **Implement comprehensive health checks** for monitoring
6. **Use resource limits** to prevent resource exhaustion
7. **Monitor container metrics** for performance optimization
8. **Regular security updates** of base images and dependencies