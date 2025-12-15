# Swagger API Documentation

The SNPedia application now includes comprehensive API documentation using Swagger/OpenAPI 3.0.

## Accessing the Documentation

### Swagger UI
- **URL**: `/api/v1/docs/`
- **Redirect**: `/swagger` (redirects to the full documentation)
- **Description**: Interactive API documentation with the ability to test endpoints directly

### API Endpoints

The Swagger documentation covers all available API endpoints organized into namespaces:

#### RSIDs (`/api/v1/rsids`)
- `GET /api/v1/rsids` - Get enriched SNP data with optional pagination

#### Statistics (`/api/v1/statistics`)
- `GET /api/v1/statistics` - Get genetic data statistics (total, interesting, uncommon SNPs)
- `GET /api/v1/statistics/config` - Get non-sensitive configuration information
- `GET /api/v1/statistics/health` - Comprehensive health check with data status, config validation, and cache info

#### Cache (`/api/v1/cache`)
- `GET /api/v1/cache/stats` - Get cache statistics
- `POST /api/v1/cache/clear` - Clear all cache entries
- `POST /api/v1/cache/invalidate/<filename>` - Invalidate cache for specific file

## Features

- **Interactive Testing**: Test API endpoints directly from the browser
- **Request/Response Examples**: See example requests and responses
- **Parameter Documentation**: Detailed parameter descriptions and validation
- **Response Models**: Structured response schemas
- **Error Handling**: Documented error responses

## Usage Examples

### Pagination
```bash
# Get first page with 50 items
curl "http://localhost:5000/api/v1/rsids?page=1&page_size=50"

# Get all results (no pagination)
curl "http://localhost:5000/api/v1/rsids"
```

### Statistics
```bash
# Get genetic data statistics (returns total, interesting, uncommon counts)
curl "http://localhost:5000/api/v1/statistics"

# Get configuration information
curl "http://localhost:5000/api/v1/statistics/config"

# Comprehensive health check
curl "http://localhost:5000/api/v1/statistics/health"
```

### Cache Management
```bash
# Get cache statistics
curl "http://localhost:5000/api/v1/cache/stats"

# Clear all cache
curl -X POST "http://localhost:5000/api/v1/cache/clear"
```

## Development

The Swagger documentation is automatically generated from the Flask-RESTX decorators and models defined in `SNPedia/api/swagger_routes.py`.

### Adding New Endpoints

1. Define response models using `api.model()`
2. Create resource classes inheriting from `Resource`
3. Use decorators like `@api.doc()` and `@api.marshal_with()` for documentation
4. Add the resource to the appropriate namespace

### Response Models

All API responses are documented with structured models that match the actual application responses:

#### Statistics Response
- `total`: Total number of SNPs
- `interesting`: Number of interesting SNPs  
- `uncommon`: Number of uncommon SNPs
- `message`: Optional message (only included when present)

#### Health Check Response
- `status`: Health status (healthy/degraded/unhealthy)
- `data_loaded`: Whether genetic data is loaded
- `data_count`: Number of data items loaded
- `config_valid`: Configuration validation status
- `config_warnings`: List of configuration warnings
- `version`: Application version
- `cache`: Cache statistics object

#### Cache Statistics
- `size`: Current cache size
- `max_size`: Maximum cache capacity
- `hits`/`misses`: Cache performance metrics
- `hit_rate`: Hit rate percentage
- `total_requests`: Total cache requests

#### RSID/SNP Response
- `Name`: RS identifier (e.g., "rs1234567")
- `Description`: SNPedia description of the SNP
- `Genotype`: Personal genotype (e.g., "AA", "AG", "GG")
- `Variations`: HTML-formatted variation information from SNPedia
- `StabilizedOrientation`: Stabilized orientation from SNPedia
- `IsInteresting`: Whether SNP is interesting ("Yes"/"No")
- `IsUncommon`: Whether the genotype is uncommon ("Yes"/"No")

This ensures the Swagger documentation accurately reflects the actual API responses.