"""
Starlink Metrics REST API

FastAPI-based REST API for accessing connection metrics, diagnostics,
and reports.

Endpoints:
    GET  /                      - API information and available endpoints
    GET  /health                - Health check endpoint
    GET  /metrics/current       - Get current connection metrics
    GET  /metrics/status        - Get current connection status
    POST /metrics/diagnose      - Run diagnostics on connection
    GET  /metrics/report        - Generate metrics report
    GET  /metrics/export        - Export metrics in various formats
    GET  /config                - Get current configuration
    PUT  /config                - Update configuration
    GET  /prometheus            - Prometheus metrics endpoint
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import uvicorn

from starlink_metrics import (
    ConnectionMetrics,
    StarlinkConnectionQuality,
    QualityThresholds,
    StabilityThresholds,
    AlertThresholds,
)
from observability import MetricsExporter, StructuredLogger, PeriodicReporter


# API Models
class MetricsInput(BaseModel):
    """Input model for connection metrics."""
    packet_loss: float = Field(..., ge=0, le=100, description="Packet loss percentage (0-100)")
    latency: float = Field(..., ge=0, description="Latency in milliseconds")


class StatusResponse(BaseModel):
    """Response model for connection status."""
    status: str
    quality_score: float
    stability_score: float
    packet_loss: float
    latency: float
    service_level: str
    timestamp: str


class DiagnosticResponse(BaseModel):
    """Response model for diagnostic results."""
    status: str
    metrics: Dict[str, Any]
    assessments: Dict[str, Any]
    recommendations: List[str]
    timestamp: str


class ConfigResponse(BaseModel):
    """Response model for configuration."""
    quality_thresholds: Dict[str, float]
    stability_thresholds: Dict[str, float]
    alert_thresholds: Dict[str, float]


# Initialize FastAPI app
app = FastAPI(
    title="Starlink Metrics API",
    description="REST API for Starlink connection metrics monitoring and diagnostics",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global state (in production, use proper state management/database)
reporter = PeriodicReporter()
logger = StructuredLogger("api")


def get_sample_metrics() -> ConnectionMetrics:
    """Get sample metrics (replace with actual data source in production)."""
    return ConnectionMetrics(packet_loss=3.5, latency=95.0)


@app.get("/", tags=["info"])
async def root():
    """API information and available endpoints."""
    return {
        "name": "Starlink Metrics API",
        "version": "1.0.0",
        "description": "REST API for connection metrics monitoring",
        "endpoints": {
            "health": "/health",
            "current_metrics": "/metrics/current",
            "status": "/metrics/status",
            "diagnose": "/metrics/diagnose",
            "report": "/metrics/report",
            "export": "/metrics/export",
            "config": "/config",
            "prometheus": "/prometheus",
            "documentation": "/docs"
        }
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "starlink-metrics-api"
    }


@app.get("/metrics/current", tags=["metrics"])
async def get_current_metrics():
    """Get current raw connection metrics."""
    metrics = get_sample_metrics()
    return {
        "packet_loss": metrics.packet_loss,
        "latency": metrics.latency,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/metrics/status", response_model=StatusResponse, tags=["metrics"])
async def get_status():
    """Get current connection status with quality and stability scores."""
    metrics = get_sample_metrics()
    quality = StarlinkConnectionQuality(metrics)
    status = quality.get_connection_status()
    
    # Record for reporting
    reporter.record_metrics(status)
    
    # Log the status
    logger.log_metrics(status)
    
    status["timestamp"] = datetime.utcnow().isoformat() + "Z"
    return status


@app.post("/metrics/diagnose", response_model=DiagnosticResponse, tags=["metrics"])
async def diagnose_connection(metrics_input: Optional[MetricsInput] = None):
    """
    Run comprehensive diagnostics on connection.
    
    Optionally provide custom metrics, otherwise uses current metrics.
    """
    if metrics_input:
        metrics = ConnectionMetrics(
            packet_loss=metrics_input.packet_loss,
            latency=metrics_input.latency
        )
    else:
        metrics = get_sample_metrics()
    
    quality = StarlinkConnectionQuality(metrics)
    status = quality.get_connection_status()
    
    # Build diagnostic response
    assessments = {
        "packet_loss": {
            "value": status['packet_loss'],
            "status": "good" if status['packet_loss'] <= 5 else "warning" if status['packet_loss'] <= 10 else "critical",
            "threshold": 5.0
        },
        "latency": {
            "value": status['latency'],
            "status": "good" if status['latency'] <= 150 else "warning" if status['latency'] <= 250 else "critical",
            "threshold": 150.0
        },
        "quality": {
            "score": status['quality_score'],
            "status": "excellent" if status['quality_score'] >= 90 else "good" if status['quality_score'] >= 75 else "fair" if status['quality_score'] >= 50 else "poor"
        },
        "stability": {
            "score": status['stability_score'],
            "service_level": status['service_level']
        }
    }
    
    # Generate recommendations
    recommendations = []
    if status['packet_loss'] > 10:
        recommendations.append("High packet loss detected - check for physical obstructions to satellite dish")
        recommendations.append("Verify dish alignment and cable connections")
    if status['latency'] > 200:
        recommendations.append("High latency detected - check for network congestion")
        recommendations.append("Consider traffic prioritization or QoS settings")
    if status['service_level'] in ['Critical', 'Offline']:
        recommendations.append("Connection is in critical state - immediate action required")
        recommendations.append("Consider failover to backup connection")
    if not recommendations:
        recommendations.append("No issues detected - connection is performing optimally")
    
    return {
        "status": status['status'],
        "metrics": {
            "packet_loss": status['packet_loss'],
            "latency": status['latency'],
            "quality_score": status['quality_score'],
            "stability_score": status['stability_score']
        },
        "assessments": assessments,
        "recommendations": recommendations,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@app.get("/metrics/report", tags=["metrics"])
async def get_report(
    sla_quality: float = Query(85.0, description="SLA quality score threshold"),
    sla_stability: float = Query(0.75, description="SLA stability score threshold")
):
    """Generate metrics report with SLA compliance checking."""
    sla_thresholds = {
        "quality_score": sla_quality,
        "stability_score": sla_stability
    }
    
    report = reporter.generate_report(sla_thresholds=sla_thresholds)
    return report


@app.get("/metrics/export", tags=["metrics"])
async def export_metrics(
    format: str = Query("json", description="Export format: json, prometheus, cloudwatch"),
    instance: str = Query("default", description="Instance label (for Prometheus)"),
    namespace: str = Query("Starlink/Metrics", description="Namespace (for CloudWatch)")
):
    """Export current metrics in various formats."""
    metrics = get_sample_metrics()
    quality = StarlinkConnectionQuality(metrics)
    status = quality.get_connection_status()
    
    exporter = MetricsExporter()
    
    if format == "prometheus":
        output = exporter.export_prometheus(status, labels={"instance": instance})
        return PlainTextResponse(content=output, media_type="text/plain")
    
    elif format == "cloudwatch":
        output = exporter.export_cloudwatch(status, namespace=namespace)
        return output
    
    elif format == "json":
        return status
    
    else:
        raise HTTPException(status_code=400, detail=f"Unknown format: {format}")


@app.get("/config", response_model=ConfigResponse, tags=["configuration"])
async def get_config():
    """Get current configuration."""
    return {
        "quality_thresholds": {
            "packet_loss_threshold": 5.0,
            "latency_threshold": 150.0,
            "packet_loss_penalty": 10.0,
            "latency_penalty": 5.0
        },
        "stability_thresholds": {
            "max_latency": 500.0,
            "packet_loss_weight": 0.7,
            "latency_weight": 0.3,
            "packet_loss_multiplier": 2.0
        },
        "alert_thresholds": {
            "critical_stability": 0.3,
            "degraded_stability": 0.5,
            "stable_stability": 0.7
        }
    }


@app.put("/config", tags=["configuration"])
async def update_config(config: ConfigResponse):
    """
    Update configuration.
    
    Note: In production, implement proper validation and persistence.
    """
    # TODO: Implement configuration persistence
    # For now, just validate the input
    return {
        "message": "Configuration update received",
        "config": config,
        "note": "Persistence not yet implemented - configuration is not saved"
    }


@app.get("/prometheus", tags=["monitoring"])
async def prometheus_metrics():
    """Prometheus metrics endpoint for scraping."""
    metrics = get_sample_metrics()
    quality = StarlinkConnectionQuality(metrics)
    status = quality.get_connection_status()
    
    exporter = MetricsExporter()
    output = exporter.export_prometheus(status, labels={"service": "starlink-metrics-api"})
    
    return PlainTextResponse(content=output, media_type="text/plain")


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors."""
    return JSONResponse(
        status_code=400,
        content={"error": "Validation error", "detail": str(exc)}
    )


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Start the API server."""
    uvicorn.run(
        "starlink_api:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    import sys
    
    # Simple argument parsing for standalone execution
    host = "0.0.0.0"
    port = 8000
    reload = False
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith("--host="):
                host = arg.split("=")[1]
            elif arg.startswith("--port="):
                port = int(arg.split("=")[1])
            elif arg == "--reload":
                reload = True
    
    print(f"Starting Starlink Metrics API on {host}:{port}")
    print(f"API documentation available at http://{host}:{port}/docs")
    start_server(host=host, port=port, reload=reload)
