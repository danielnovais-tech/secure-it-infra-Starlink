"""
Tests for Starlink Metrics CLI and REST API
"""

import pytest
import json
import sys
from io import StringIO
from unittest.mock import patch, MagicMock

# CLI tests
from starlink_cli import (
    cmd_status,
    cmd_check,
    cmd_export,
    cmd_config,
    get_current_metrics
)

# API tests
from fastapi.testclient import TestClient
from starlink_api import app


class TestCLI:
    """Tests for CLI commands."""
    
    def test_get_current_metrics(self):
        """Test that get_current_metrics returns valid ConnectionMetrics."""
        metrics = get_current_metrics()
        assert 0 <= metrics.packet_loss <= 100
        assert metrics.latency >= 0
    
    def test_cmd_status_text_output(self, capsys):
        """Test status command with text output."""
        args = MagicMock()
        args.json = False
        
        cmd_status(args)
        
        captured = capsys.readouterr()
        assert "STARLINK CONNECTION STATUS" in captured.out
        assert "Quality Score:" in captured.out
        assert "Stability Score:" in captured.out
    
    def test_cmd_status_json_output(self, capsys):
        """Test status command with JSON output."""
        args = MagicMock()
        args.json = True
        
        cmd_status(args)
        
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        
        assert "quality_score" in output
        assert "stability_score" in output
        assert "service_level" in output
    
    def test_cmd_check(self, capsys):
        """Test check/diagnostics command."""
        args = MagicMock()
        
        cmd_check(args)
        
        captured = capsys.readouterr()
        assert "DIAGNOSTIC RESULTS" in captured.out
        assert "CONNECTION METRICS" in captured.out
        assert "QUALITY ASSESSMENT" in captured.out
        assert "STABILITY ASSESSMENT" in captured.out
        assert "RECOMMENDATIONS" in captured.out
    
    def test_cmd_export_json(self, capsys):
        """Test export command with JSON format."""
        args = MagicMock()
        args.format = 'json'
        args.instance = 'test'
        args.namespace = 'Test/Metrics'
        
        cmd_export(args)
        
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        
        assert "quality_score" in output
        assert "stability_score" in output
    
    def test_cmd_export_prometheus(self, capsys):
        """Test export command with Prometheus format."""
        args = MagicMock()
        args.format = 'prometheus'
        args.instance = 'test'
        args.namespace = 'Test/Metrics'
        
        cmd_export(args)
        
        captured = capsys.readouterr()
        assert "starlink_connection_quality_score" in captured.out
        assert "starlink_connection_stability_score" in captured.out
    
    def test_cmd_export_cloudwatch(self, capsys):
        """Test export command with CloudWatch format."""
        args = MagicMock()
        args.format = 'cloudwatch'
        args.instance = 'test'
        args.namespace = 'Test/Metrics'
        
        cmd_export(args)
        
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        
        assert "Namespace" in output
        assert "MetricData" in output
    
    def test_cmd_config_show(self, capsys):
        """Test config command."""
        args = MagicMock()
        args.show = True
        
        cmd_config(args)
        
        captured = capsys.readouterr()
        config = json.loads(captured.out)
        
        assert "quality_thresholds" in config
        assert "stability_thresholds" in config
        assert "alert_thresholds" in config


class TestAPI:
    """Tests for REST API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Starlink Metrics API"
        assert "endpoints" in data
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_get_current_metrics(self, client):
        """Test current metrics endpoint."""
        response = client.get("/metrics/current")
        assert response.status_code == 200
        data = response.json()
        assert "packet_loss" in data
        assert "latency" in data
        assert "timestamp" in data
    
    def test_get_status(self, client):
        """Test status endpoint."""
        response = client.get("/metrics/status")
        assert response.status_code == 200
        data = response.json()
        assert "quality_score" in data
        assert "stability_score" in data
        assert "service_level" in data
        assert "status" in data
    
    def test_diagnose_connection_default(self, client):
        """Test diagnose endpoint with default metrics."""
        response = client.post("/metrics/diagnose")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "metrics" in data
        assert "assessments" in data
        assert "recommendations" in data
    
    def test_diagnose_connection_custom(self, client):
        """Test diagnose endpoint with custom metrics."""
        payload = {
            "packet_loss": 15.0,
            "latency": 250.0
        }
        response = client.post("/metrics/diagnose", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["metrics"]["packet_loss"] == 15.0
        assert data["metrics"]["latency"] == 250.0
        assert len(data["recommendations"]) > 0
    
    def test_diagnose_invalid_packet_loss(self, client):
        """Test diagnose with invalid packet loss."""
        payload = {
            "packet_loss": 150.0,  # Invalid: > 100
            "latency": 100.0
        }
        response = client.post("/metrics/diagnose", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_diagnose_negative_latency(self, client):
        """Test diagnose with negative latency."""
        payload = {
            "packet_loss": 5.0,
            "latency": -10.0  # Invalid: negative
        }
        response = client.post("/metrics/diagnose", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_get_report(self, client):
        """Test report endpoint."""
        response = client.get("/metrics/report")
        assert response.status_code == 200
        data = response.json()
        assert "total_measurements" in data
        assert "summary" in data
    
    def test_get_report_custom_sla(self, client):
        """Test report endpoint with custom SLA thresholds."""
        response = client.get("/metrics/report?sla_quality=90.0&sla_stability=0.8")
        assert response.status_code == 200
        data = response.json()
        assert "sla_compliance" in data
    
    def test_export_json(self, client):
        """Test export endpoint with JSON format."""
        response = client.get("/metrics/export?format=json")
        assert response.status_code == 200
        data = response.json()
        assert "quality_score" in data
    
    def test_export_prometheus(self, client):
        """Test export endpoint with Prometheus format."""
        response = client.get("/metrics/export?format=prometheus")
        assert response.status_code == 200
        assert "starlink_connection_quality_score" in response.text
    
    def test_export_cloudwatch(self, client):
        """Test export endpoint with CloudWatch format."""
        response = client.get("/metrics/export?format=cloudwatch")
        assert response.status_code == 200
        data = response.json()
        assert "Namespace" in data
    
    def test_export_invalid_format(self, client):
        """Test export endpoint with invalid format."""
        response = client.get("/metrics/export?format=invalid")
        assert response.status_code == 400
    
    def test_get_config(self, client):
        """Test get configuration endpoint."""
        response = client.get("/config")
        assert response.status_code == 200
        data = response.json()
        assert "quality_thresholds" in data
        assert "stability_thresholds" in data
        assert "alert_thresholds" in data
    
    def test_update_config(self, client):
        """Test update configuration endpoint."""
        config = {
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
        response = client.put("/config", json=config)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
    
    def test_prometheus_endpoint(self, client):
        """Test Prometheus metrics endpoint."""
        response = client.get("/prometheus")
        assert response.status_code == 200
        assert "starlink_connection_quality_score" in response.text
        assert "starlink_connection_stability_score" in response.text
