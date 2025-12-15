# Prometheus Metrics

SNPedia now includes a Prometheus metrics endpoint for monitoring application performance and usage.

## Metrics Endpoint

The metrics are available at:
- Development (Flask dev server): `http://localhost:5000/metrics`
- Production/Docker (Gunicorn): `http://localhost:8080/metrics`

## Available Metrics

### HTTP Metrics

- **`http_requests_total`** - Total number of HTTP requests
  - Labels: `method`, `endpoint`, `status`
- **`http_request_duration_seconds`** - HTTP request duration in seconds
  - Labels: `method`, `endpoint`
- **`http_request_size_bytes`** - HTTP request size in bytes
  - Labels: `method`, `endpoint`
- **`http_response_size_bytes`** - HTTP response size in bytes
  - Labels: `method`, `endpoint`, `status`

### Application-Specific Metrics

- **`snp_queries_total`** - Total number of SNP queries processed
  - Labels: `query_type` (values: `all`, `paginated`, `statistics`, `cache_stats`, `cache_clear`)
- **`cache_hits_total`** - Total number of cache hits
  - Labels: `cache_type` (values: `data_cache`)
- **`cache_misses_total`** - Total number of cache misses
  - Labels: `cache_type` (values: `data_cache`)
- **`application_errors_total`** - Total number of application errors
  - Labels: `error_type`, `endpoint`
- **`rsid_counts`** - Number of RSIDs by category
  - Labels: `category` (values: `total`, `interesting`, `uncommon`)

## Usage Examples

### Basic Monitoring

```bash
# Get all metrics (development)
curl http://localhost:5000/metrics

# Get all metrics (Docker/production)
curl http://localhost:8080/metrics

# Filter specific metrics
curl http://localhost:8080/metrics | grep snp_queries_total
```

### Prometheus Configuration

Add this job to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'snpedia'
    static_configs:
      - targets: ['localhost:8080']  # Use 8080 for Docker, 5000 for development
    metrics_path: '/metrics'
    scrape_interval: 15s
```

### Grafana Dashboard Queries

#### Request Rate
```promql
rate(http_requests_total[5m])
```

#### Error Rate
```promql
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
```

#### Cache Hit Rate
```promql
rate(cache_hits_total[5m]) / (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))
```

#### SNP Query Rate by Type
```promql
rate(snp_queries_total[5m])
```

#### Response Time Percentiles
```promql
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

#### RSID Counts
```promql
# Total RSIDs
rsid_counts{category="total"}

# Interesting RSIDs
rsid_counts{category="interesting"}

# Uncommon RSIDs
rsid_counts{category="uncommon"}
```

#### RSID Ratios
```promql
# Percentage of interesting RSIDs
(rsid_counts{category="interesting"} / rsid_counts{category="total"}) * 100

# Percentage of uncommon RSIDs
(rsid_counts{category="uncommon"} / rsid_counts{category="total"}) * 100
```

## Docker Considerations

When running in Docker, ensure the metrics endpoint is accessible:

```yaml
# docker-compose.yml
services:
  osgenome:
    ports:
      - "8080:8080"  # Expose metrics endpoint (production)
      # or "5000:5000" for development
```

## Security Notes

- The metrics endpoint exposes application performance data
- Consider restricting access in production environments
- No sensitive data is exposed through metrics
- Metrics collection has minimal performance impact

## Troubleshooting

### Metrics Not Available

If the `/metrics` endpoint returns 404:
1. Ensure `prometheus-client` is installed
2. Check that metrics are initialized in `app.py`
3. Verify no errors in application logs

### Missing Metrics

If specific metrics are missing:
1. Check that the relevant code paths are being executed
2. Verify metrics are being recorded in the application logs
3. Ensure proper labels are being used

### High Memory Usage

If metrics collection causes memory issues:
1. Consider reducing metric retention time
2. Limit the number of unique label combinations
3. Monitor the `/metrics` endpoint size