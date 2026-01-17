"""
Unit tests for observability module.
"""

import pytest
import json
from observability import MetricsExporter, StructuredLogger, PeriodicReporter


class TestMetricsExporter:
    """Test MetricsExporter class."""
    
    def test_prometheus_export_basic(self):
        """Test basic Prometheus export."""
        status = {
            "quality_score": 95.0,
            "stability_score": 0.88,
            "packet_loss": 3.0,
            "latency": 110.0,
            "service_level": "Stable",
            "status": "Excellent"
        }
        
        exporter = MetricsExporter()
        output = exporter.export_prometheus(status)
        
        assert "starlink_connection_quality_score 95.0" in output
        assert "starlink_connection_stability_score 0.880" in output
        assert "starlink_connection_packet_loss_percent 3.0" in output
        assert "starlink_connection_latency_ms 110.0" in output
        assert "starlink_connection_service_level 3" in output  # Stable = 3
        assert "starlink_connection_alert_level 0" in output  # No alert
    
    def test_prometheus_export_with_labels(self):
        """Test Prometheus export with custom labels."""
        status = {
            "quality_score": 85.0,
            "stability_score": 0.75,
            "packet_loss": 8.0,
            "latency": 170.0,
            "service_level": "Stable",
            "status": "Good"
        }
        
        exporter = MetricsExporter()
        output = exporter.export_prometheus(status, labels={"datacenter": "us-west", "instance": "sat-01"})
        
        assert 'datacenter="us-west"' in output
        assert 'instance="sat-01"' in output
    
    def test_prometheus_export_with_alert(self):
        """Test Prometheus export with alert."""
        status = {
            "quality_score": 85.0,
            "stability_score": 0.45,
            "packet_loss": 22.0,
            "latency": 360.0,
            "service_level": "Degraded",
            "status": "Fair",
            "alert_level": "degraded"
        }
        
        exporter = MetricsExporter()
        output = exporter.export_prometheus(status)
        
        assert "starlink_connection_alert_level 1" in output  # degraded = 1
        assert "starlink_connection_service_level 2" in output  # Degraded = 2
    
    def test_cloudwatch_export_basic(self):
        """Test basic CloudWatch export."""
        status = {
            "quality_score": 90.0,
            "stability_score": 0.82,
            "packet_loss": 5.5,
            "latency": 125.0,
            "service_level": "Stable",
            "status": "Good"
        }
        
        exporter = MetricsExporter()
        output = exporter.export_cloudwatch(status)
        
        assert output["Namespace"] == "Starlink/Connection"
        assert len(output["MetricData"]) == 4
        
        # Check metric values
        metrics_dict = {m["MetricName"]: m for m in output["MetricData"]}
        assert metrics_dict["QualityScore"]["Value"] == 90.0
        assert metrics_dict["StabilityScore"]["Value"] == 0.82
        assert metrics_dict["PacketLoss"]["Value"] == 5.5
        assert metrics_dict["Latency"]["Value"] == 125.0
    
    def test_cloudwatch_export_custom_namespace(self):
        """Test CloudWatch export with custom namespace."""
        status = {
            "quality_score": 90.0,
            "stability_score": 0.82,
            "packet_loss": 5.5,
            "latency": 125.0,
            "service_level": "Stable",
            "status": "Good"
        }
        
        exporter = MetricsExporter()
        output = exporter.export_cloudwatch(status, namespace="CustomNamespace/Metrics")
        
        assert output["Namespace"] == "CustomNamespace/Metrics"
    
    def test_service_level_to_value_mapping(self):
        """Test service level to numeric value mapping."""
        exporter = MetricsExporter()
        
        assert exporter._service_level_to_value("Offline") == 0
        assert exporter._service_level_to_value("Critical") == 1
        assert exporter._service_level_to_value("Degraded") == 2
        assert exporter._service_level_to_value("Stable") == 3
        assert exporter._service_level_to_value("Unknown") == 0  # Default


class TestStructuredLogger:
    """Test StructuredLogger class."""
    
    def test_log_alert_critical(self):
        """Test logging a critical alert."""
        import logging
        from io import StringIO
        
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        
        logger = StructuredLogger("test_logger")
        logger.logger.handlers = [handler]
        logger.logger.setLevel(logging.INFO)
        
        logger.log_alert("critical", {
            "stability": 0.25,
            "service_level": "Critical",
            "packet_loss": 35.0,
            "latency": 450.0
        })
        
        log_output = log_stream.getvalue()
        log_data = json.loads(log_output.strip())
        
        assert log_data["event_type"] == "connection_alert"
        assert log_data["alert_level"] == "critical"
        assert log_data["severity"] == "HIGH"
        assert log_data["stability"] == 0.25
        assert log_data["service_level"] == "Critical"
    
    def test_log_alert_degraded(self):
        """Test logging a degraded alert."""
        import logging
        from io import StringIO
        
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        
        logger = StructuredLogger("test_logger2")
        logger.logger.handlers = [handler]
        logger.logger.setLevel(logging.INFO)
        
        logger.log_alert("degraded", {
            "stability": 0.48,
            "service_level": "Degraded",
            "packet_loss": 18.0,
            "latency": 280.0
        })
        
        log_output = log_stream.getvalue()
        log_data = json.loads(log_output.strip())
        
        assert log_data["alert_level"] == "degraded"
        assert log_data["severity"] == "MEDIUM"
    
    def test_log_status_change(self):
        """Test logging status change."""
        import logging
        from io import StringIO
        
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        
        logger = StructuredLogger("test_logger3")
        logger.logger.handlers = [handler]
        logger.logger.setLevel(logging.INFO)
        
        logger.log_status_change("Good", "Fair", {
            "quality_score": 75.0,
            "stability_score": 0.65,
            "service_level": "Degraded"
        })
        
        log_output = log_stream.getvalue()
        log_data = json.loads(log_output.strip())
        
        assert log_data["event_type"] == "status_change"
        assert log_data["old_status"] == "Good"
        assert log_data["new_status"] == "Fair"


class TestPeriodicReporter:
    """Test PeriodicReporter class."""
    
    def test_record_and_generate_report(self):
        """Test recording metrics and generating report."""
        reporter = PeriodicReporter()
        
        # Record metrics
        reporter.record_metrics({
            "quality_score": 95.0,
            "stability_score": 0.90,
            "packet_loss": 2.0,
            "latency": 80.0,
            "service_level": "Stable",
            "status": "Excellent"
        })
        reporter.record_metrics({
            "quality_score": 85.0,
            "stability_score": 0.80,
            "packet_loss": 6.0,
            "latency": 140.0,
            "service_level": "Stable",
            "status": "Good"
        })
        
        report = reporter.generate_report()
        
        assert report["total_measurements"] == 2
        assert report["summary"]["quality_score"]["avg"] == pytest.approx(90.0, rel=0.01)
        assert report["summary"]["stability_score"]["avg"] == pytest.approx(0.85, rel=0.01)
        assert report["service_level_distribution"]["Stable"] == 2
        assert report["uptime_percentage"] == 100.0
    
    def test_sla_compliance_check(self):
        """Test SLA compliance checking."""
        reporter = PeriodicReporter()
        
        # Record metrics
        reporter.record_metrics({
            "quality_score": 90.0,
            "stability_score": 0.75,
            "packet_loss": 5.0,
            "latency": 120.0,
            "service_level": "Stable",
            "status": "Good"
        })
        reporter.record_metrics({
            "quality_score": 80.0,
            "stability_score": 0.65,
            "packet_loss": 10.0,
            "latency": 180.0,
            "service_level": "Degraded",
            "status": "Fair"
        })
        
        report = reporter.generate_report(sla_thresholds={
            "quality_score": 85,
            "stability_score": 0.7
        })
        
        assert "sla_compliance" in report
        # Average quality is 85.0, exactly at threshold
        assert report["sla_compliance"]["quality_score"]["compliant"] is True
        # Average stability is 0.7, exactly at threshold
        assert report["sla_compliance"]["stability_score"]["compliant"] is True
    
    def test_empty_buffer_report(self):
        """Test generating report with empty buffer."""
        reporter = PeriodicReporter()
        report = reporter.generate_report()
        
        assert "error" in report
        assert report["error"] == "No metrics recorded"
    
    def test_clear_buffer(self):
        """Test clearing metrics buffer."""
        reporter = PeriodicReporter()
        
        reporter.record_metrics({
            "quality_score": 90.0,
            "stability_score": 0.85,
            "packet_loss": 5.0,
            "latency": 120.0,
            "service_level": "Stable",
            "status": "Good"
        })
        
        assert len(reporter.metrics_buffer) == 1
        
        reporter.clear_buffer()
        assert len(reporter.metrics_buffer) == 0
    
    def test_service_level_distribution(self):
        """Test service level distribution in report."""
        reporter = PeriodicReporter()
        
        # Add varied service levels
        service_levels = ["Stable", "Stable", "Degraded", "Critical", "Stable"]
        for sl in service_levels:
            reporter.record_metrics({
                "quality_score": 80.0,
                "stability_score": 0.7,
                "packet_loss": 5.0,
                "latency": 100.0,
                "service_level": sl,
                "status": "Good"
            })
        
        report = reporter.generate_report()
        
        assert report["service_level_distribution"]["Stable"] == 3
        assert report["service_level_distribution"]["Degraded"] == 1
        assert report["service_level_distribution"]["Critical"] == 1
        assert report["service_level_distribution"]["Offline"] == 0
    
    def test_uptime_calculation(self):
        """Test uptime percentage calculation."""
        reporter = PeriodicReporter()
        
        # 3 stable, 1 degraded, 1 critical = 60% uptime
        reporter.record_metrics({"quality_score": 90, "stability_score": 0.9, "packet_loss": 1, "latency": 50, "service_level": "Stable", "status": "Good"})
        reporter.record_metrics({"quality_score": 90, "stability_score": 0.9, "packet_loss": 1, "latency": 50, "service_level": "Stable", "status": "Good"})
        reporter.record_metrics({"quality_score": 90, "stability_score": 0.9, "packet_loss": 1, "latency": 50, "service_level": "Stable", "status": "Good"})
        reporter.record_metrics({"quality_score": 70, "stability_score": 0.6, "packet_loss": 15, "latency": 250, "service_level": "Degraded", "status": "Fair"})
        reporter.record_metrics({"quality_score": 50, "stability_score": 0.4, "packet_loss": 25, "latency": 400, "service_level": "Critical", "status": "Poor"})
        
        report = reporter.generate_report()
        
        assert report["uptime_percentage"] == 60.0
