"""Prometheus metrics definitions for SonicLibrary.

All application metrics are defined here so they can be imported
wherever instrumentation is needed.
"""

from prometheus_client import Counter, Histogram, Gauge

# --- HTTP metrics (instrumented in RequestLoggingMiddleware) ---

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
)

# --- External API metrics ---

external_api_requests_total = Counter(
    "external_api_requests_total",
    "Total external API requests",
    ["service", "status"],
)

external_api_duration_seconds = Histogram(
    "external_api_duration_seconds",
    "External API request duration in seconds",
    ["service"],
)

# --- Cache metrics ---

cache_operations_total = Counter(
    "cache_operations_total",
    "Total cache operations",
    ["cache", "result"],
)

# --- Recommendation metrics ---

recommendation_generation_duration_seconds = Histogram(
    "recommendation_generation_duration_seconds",
    "Duration of recommendation generation in seconds",
)

# --- Circuit breaker metrics ---

circuit_breaker_state = Gauge(
    "circuit_breaker_state",
    "Circuit breaker state: 0=closed, 1=open, 2=half-open",
    ["service"],
)
