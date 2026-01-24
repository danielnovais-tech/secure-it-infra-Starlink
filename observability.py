"""
Observability module for Starlink Connection Metrics.

Provides Prometheus metrics export and structured logging capabilities.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional
from collections import defaultdict


class MetricsExporter:
    """
    Export connection metrics in Prometheus format.

    Provides methods to format metrics for Prometheus scraping and
    track metrics over time.
    """

    def __init__(self):
        """Initialize the metrics exporter."""
        self.metrics_history = defaultdict(list)

    def export_prometheus(
        self, status: Dict, labels: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Export metrics in Prometheus text format.

        Args:
            status: Connection status dictionary from get_connection_status()
            labels: Optional labels to add to metrics (e.g., {"location": "datacenter1"})

        Returns:
            Prometheus-formatted metrics string
        """
        labels_str = self._format_labels(labels or {})
        timestamp = int(datetime.utcnow().timestamp() * 1000)

        metrics = []

        # Quality score (0-100)
        metrics.append(
            f'starlink_connection_quality_score{labels_str} {status["quality_score"]} {timestamp}'
        )

        # Stability score (0.0-1.0)
        metrics.append(
            f'starlink_connection_stability_score{labels_str} {status["stability_score"]:.3f} {timestamp}'
        )

        # Packet loss percentage
        metrics.append(
            f'starlink_connection_packet_loss_percent{labels_str} {status["packet_loss"]} {timestamp}'
        )

        # Latency in milliseconds
        metrics.append(
            f'starlink_connection_latency_ms{labels_str} {status["latency"]} {timestamp}'
        )

        # Service level as gauge (0=Offline, 1=Critical, 2=Degraded, 3=Stable)
        service_level_value = self._service_level_to_value(status["service_level"])
        metrics.append(
            f"starlink_connection_service_level{labels_str} {service_level_value} {timestamp}"
        )

        # Alert status (0=no alert, 1=degraded, 2=critical)
        alert_value = 0
        if status.get("alert_level") == "degraded":
            alert_value = 1
        elif status.get("alert_level") == "critical":
            alert_value = 2
        metrics.append(
            f"starlink_connection_alert_level{labels_str} {alert_value} {timestamp}"
        )

        return "\n".join(metrics) + "\n"

    def export_cloudwatch(
        self, status: Dict, namespace: str = "Starlink/Connection"
    ) -> Dict:
        """
        Export metrics in AWS CloudWatch format.

        Args:
            status: Connection status dictionary from get_connection_status()
            namespace: CloudWatch namespace (default: "Starlink/Connection")

        Returns:
            Dictionary formatted for CloudWatch PutMetricData API
        """
        timestamp = datetime.utcnow()

        metric_data = []

        # Quality score
        metric_data.append(
            {
                "MetricName": "QualityScore",
                "Value": status["quality_score"],
                "Unit": "None",
                "Timestamp": timestamp,
            }
        )

        # Stability score
        metric_data.append(
            {
                "MetricName": "StabilityScore",
                "Value": status["stability_score"],
                "Unit": "None",
                "Timestamp": timestamp,
            }
        )

        # Packet loss
        metric_data.append(
            {
                "MetricName": "PacketLoss",
                "Value": status["packet_loss"],
                "Unit": "Percent",
                "Timestamp": timestamp,
            }
        )

        # Latency
        metric_data.append(
            {
                "MetricName": "Latency",
                "Value": status["latency"],
                "Unit": "Milliseconds",
                "Timestamp": timestamp,
            }
        )

        return {"Namespace": namespace, "MetricData": metric_data}

    def _format_labels(self, labels: Dict[str, str]) -> str:
        """Format labels for Prometheus."""
        if not labels:
            return ""
        label_pairs = [f'{k}="{v}"' for k, v in labels.items()]
        return "{" + ",".join(label_pairs) + "}"

    def _service_level_to_value(self, service_level: str) -> int:
        """Convert service level string to numeric value."""
        mapping = {"Offline": 0, "Critical": 1, "Degraded": 2, "Stable": 3}
        return mapping.get(service_level, 0)


class StructuredLogger:
    """
    Structured JSON logger for connection metrics and alerts.

    Provides methods to log events in JSON format for SIEM integration.
    """

    def __init__(self, logger_name: str = "starlink_metrics"):
        """
        Initialize the structured logger.

        Args:
            logger_name: Name for the logger instance
        """
        self.logger = logging.getLogger(logger_name)
        self._setup_logger()

    def _setup_logger(self):
        """Setup logger with JSON formatter."""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def log_alert(self, level: str, data: Dict) -> None:
        """
        Log an alert event in structured JSON format.

        Args:
            level: Alert level ("critical", "degraded")
            data: Alert data dictionary
        """
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "connection_alert",
            "alert_level": level,
            "stability": data.get("stability"),
            "service_level": data.get("service_level"),
            "packet_loss": data.get("packet_loss"),
            "latency": data.get("latency"),
            "severity": "HIGH" if level == "critical" else "MEDIUM",
        }

        log_method = self.logger.error if level == "critical" else self.logger.warning
        log_method(json.dumps(event))

    def log_status_change(self, old_status: str, new_status: str, data: Dict) -> None:
        """
        Log a status change event.

        Args:
            old_status: Previous connection status
            new_status: New connection status
            data: Connection status data
        """
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "status_change",
            "old_status": old_status,
            "new_status": new_status,
            "quality_score": data.get("quality_score"),
            "stability_score": data.get("stability_score"),
            "service_level": data.get("service_level"),
        }

        self.logger.info(json.dumps(event))

    def log_metrics(self, status: Dict) -> None:
        """
        Log current metrics snapshot.

        Args:
            status: Connection status dictionary
        """
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "metrics_snapshot",
            "quality_score": status["quality_score"],
            "stability_score": status["stability_score"],
            "packet_loss": status["packet_loss"],
            "latency": status["latency"],
            "service_level": status["service_level"],
            "status": status["status"],
        }

        self.logger.info(json.dumps(event))


class PeriodicReporter:
    """
    Generate periodic reports for governance and auditing.

    Tracks metrics over time and generates summary reports.
    """

    def __init__(self):
        """Initialize the periodic reporter."""
        self.metrics_buffer = []

    def record_metrics(self, status: Dict) -> None:
        """
        Record metrics for reporting.

        Args:
            status: Connection status dictionary
        """
        self.metrics_buffer.append(
            {"timestamp": datetime.utcnow().isoformat() + "Z", **status}
        )

    def generate_report(self, sla_thresholds: Optional[Dict] = None) -> Dict:
        """
        Generate a summary report from recorded metrics.

        Args:
            sla_thresholds: Optional SLA thresholds for compliance checking
                          Example: {"quality_score": 85, "stability_score": 0.7}

        Returns:
            Dictionary containing report data
        """
        if not self.metrics_buffer:
            return {
                "error": "No metrics recorded",
                "report_generated_at": datetime.utcnow().isoformat() + "Z",
            }

        # Calculate statistics
        quality_scores = [m["quality_score"] for m in self.metrics_buffer]
        stability_scores = [m["stability_score"] for m in self.metrics_buffer]
        packet_losses = [m["packet_loss"] for m in self.metrics_buffer]
        latencies = [m["latency"] for m in self.metrics_buffer]

        # Service level distribution
        service_levels = [m["service_level"] for m in self.metrics_buffer]
        service_level_counts = {}
        for sl in ["Stable", "Degraded", "Critical", "Offline"]:
            service_level_counts[sl] = service_levels.count(sl)

        # Calculate uptime/SLA compliance
        total_measurements = len(self.metrics_buffer)
        stable_measurements = service_level_counts.get("Stable", 0)
        uptime_percentage = (
            (stable_measurements / total_measurements * 100)
            if total_measurements > 0
            else 0
        )

        report = {
            "report_generated_at": datetime.utcnow().isoformat() + "Z",
            "period_start": self.metrics_buffer[0]["timestamp"],
            "period_end": self.metrics_buffer[-1]["timestamp"],
            "total_measurements": total_measurements,
            "summary": {
                "quality_score": {
                    "avg": sum(quality_scores) / len(quality_scores),
                    "min": min(quality_scores),
                    "max": max(quality_scores),
                },
                "stability_score": {
                    "avg": sum(stability_scores) / len(stability_scores),
                    "min": min(stability_scores),
                    "max": max(stability_scores),
                },
                "packet_loss": {
                    "avg": sum(packet_losses) / len(packet_losses),
                    "min": min(packet_losses),
                    "max": max(packet_losses),
                },
                "latency": {
                    "avg": sum(latencies) / len(latencies),
                    "min": min(latencies),
                    "max": max(latencies),
                },
            },
            "service_level_distribution": service_level_counts,
            "uptime_percentage": uptime_percentage,
        }

        # SLA compliance check
        if sla_thresholds:
            report["sla_compliance"] = self._check_sla_compliance(
                sla_thresholds, report["summary"]
            )

        return report

    def _check_sla_compliance(self, thresholds: Dict, summary: Dict) -> Dict:
        """Check SLA compliance against thresholds."""
        compliance = {}

        if "quality_score" in thresholds:
            avg_quality = summary["quality_score"]["avg"]
            compliance["quality_score"] = {
                "threshold": thresholds["quality_score"],
                "actual": avg_quality,
                "compliant": avg_quality >= thresholds["quality_score"],
            }

        if "stability_score" in thresholds:
            avg_stability = summary["stability_score"]["avg"]
            compliance["stability_score"] = {
                "threshold": thresholds["stability_score"],
                "actual": avg_stability,
                "compliant": avg_stability >= thresholds["stability_score"],
            }

        return compliance

    def clear_buffer(self) -> None:
        """Clear the metrics buffer after report generation."""
        self.metrics_buffer = []

    def export_report_json(self, report: Dict, filename: str) -> None:
        """
        Export report to JSON file.

        Args:
            report: Report dictionary from generate_report()
            filename: Path to output file
        """
        with open(filename, "w") as f:
            json.dump(report, f, indent=2)
