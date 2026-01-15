"""
Security Scoring Module

This module provides functionality to adjust security scores based on security levels.
"""

import csv
import json
import logging
import os
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Literal, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """Exception raised for configuration validation errors."""

    pass


class SecurityLevel(Enum):
    """Enumeration of security levels for score adjustment."""

    CRITICAL = "critical"
    ELEVATED = "elevated"
    NORMAL = "normal"


# Default score multipliers for each security level
DEFAULT_SECURITY_LEVEL_MULTIPLIERS = {
    SecurityLevel.CRITICAL: 0.7,
    SecurityLevel.ELEVATED: 0.9,
    SecurityLevel.NORMAL: 1.0,
}


def validate_config_schema(config: dict) -> None:
    """
    Validate the configuration schema.

    Args:
        config (dict): Configuration dictionary to validate.

    Raises:
        ConfigValidationError: If configuration is invalid.
    """
    if not isinstance(config, dict):
        raise ConfigValidationError("Config must be a dictionary")

    if "multipliers" not in config:
        raise ConfigValidationError("Config must contain 'multipliers' key")

    multipliers = config["multipliers"]
    if not isinstance(multipliers, dict):
        raise ConfigValidationError("'multipliers' must be a dictionary")

    valid_levels = {level.value for level in SecurityLevel}

    for level_str, multiplier in multipliers.items():
        # Check valid security level
        if level_str.lower() not in valid_levels:
            raise ConfigValidationError(
                f"Invalid security level '{level_str}'. Must be one of: {', '.join(valid_levels)}"
            )

        # Check multiplier is a number
        try:
            mult_value = float(multiplier)
        except (ValueError, TypeError):
            raise ConfigValidationError(
                f"Multiplier for '{level_str}' must be a number, got: {multiplier}"
            )

        # Check multiplier is non-negative
        if mult_value < 0:
            raise ConfigValidationError(
                f"Multiplier for '{level_str}' must be non-negative, got: {mult_value}"
            )

        # Warn about unusual multipliers
        if mult_value > 2.0:
            logger.warning(
                f"Multiplier for '{level_str}' is unusually high ({mult_value}). "
                "This will increase scores, which may not be intended for security adjustments."
            )


class AuditEntry:
    """
    Represents an audit trail entry for a security scoring operation.

    Attributes:
        reason (str): Description of the scoring adjustment.
        points (str): Points adjustment details.
        security_level (str): The security level applied.
        original_score (float): The original score before adjustment.
        adjusted_score (float): The score after adjustment.
        previous_score (Optional[float]): Previous score for historical comparison.
        timestamp (str): ISO timestamp of when the entry was created.
    """

    def __init__(
        self,
        reason: str,
        points: str,
        security_level: str,
        original_score: float,
        adjusted_score: float,
        previous_score: Optional[float] = None,
        timestamp: Optional[str] = None,
    ):
        self.reason = reason
        self.points = points
        self.security_level = security_level
        self.original_score = original_score
        self.adjusted_score = adjusted_score
        self.previous_score = previous_score
        self.timestamp = timestamp or datetime.now(timezone.utc).isoformat()

    def to_dict(self, detail_level: Literal["summary", "full"] = "full") -> dict:
        """
        Convert audit entry to dictionary format.

        Args:
            detail_level (Literal["summary", "full"]): Level of detail to include.

        Returns:
            dict: Audit entry as dictionary.
        """
        if detail_level == "summary":
            return {"reason": self.reason, "adjusted_score": self.adjusted_score}
        else:  # full
            entry = {
                "reason": self.reason,
                "points": self.points,
                "security_level": self.security_level,
                "original_score": self.original_score,
                "adjusted_score": self.adjusted_score,
                "timestamp": self.timestamp,
            }
            if self.previous_score is not None:
                entry["previous_score"] = self.previous_score
                entry["historical_delta"] = self.adjusted_score - self.previous_score
            return entry

    def __repr__(self) -> str:
        return f"AuditEntry({self.to_dict()})"


class SecurityScorer:
    """
    A class to calculate security scores based on security levels.

    Attributes:
        security_level (SecurityLevel): The current security level.
        multipliers (Dict[SecurityLevel, float]): Custom multipliers for each security level.
        audit_trail (List[AuditEntry]): List of audit entries for scoring operations.
    """

    def __init__(
        self,
        security_level: SecurityLevel,
        custom_multipliers: Optional[Dict[SecurityLevel, float]] = None,
        config_file: Optional[str] = None,
    ):
        """
        Initialize the SecurityScorer with a security level.

        Args:
            security_level (SecurityLevel): The security level to use for scoring.
            custom_multipliers (Optional[Dict[SecurityLevel, float]]): Custom multiplier overrides.
            config_file (Optional[str]): Path to JSON configuration file with multipliers.

        Raises:
            ConfigValidationError: If config file exists but is invalid.
        """
        self.security_level = security_level
        self.audit_trail: List[AuditEntry] = []

        # Load multipliers from config file if provided
        if config_file and os.path.exists(config_file):
            self.multipliers = self._load_multipliers_from_config(config_file)
        elif custom_multipliers:
            self.multipliers = {
                **DEFAULT_SECURITY_LEVEL_MULTIPLIERS,
                **custom_multipliers,
            }
        else:
            self.multipliers = DEFAULT_SECURITY_LEVEL_MULTIPLIERS.copy()

    def _load_multipliers_from_config(
        self, config_file: str
    ) -> Dict[SecurityLevel, float]:
        """
        Load multipliers from a JSON configuration file with validation.

        Args:
            config_file (str): Path to the JSON configuration file.

        Returns:
            Dict[SecurityLevel, float]: Multipliers loaded from config.

        Raises:
            ConfigValidationError: If config is invalid.
        """
        try:
            with open(config_file, "r") as f:
                config = json.load(f)

            # Validate config schema
            validate_config_schema(config)

            multipliers = DEFAULT_SECURITY_LEVEL_MULTIPLIERS.copy()

            # Map string keys to SecurityLevel enum
            for level_str, multiplier in config.get("multipliers", {}).items():
                try:
                    level = SecurityLevel(level_str.lower())
                    multipliers[level] = float(multiplier)
                except (ValueError, KeyError) as e:
                    logger.warning(
                        f"Invalid security level '{level_str}' in config file: {e}"
                    )

            logger.info(f"Loaded multipliers from {config_file}")
            return multipliers

        except json.JSONDecodeError as e:
            raise ConfigValidationError(f"Invalid JSON in config file: {e}")
        except IOError as e:
            logger.warning(
                f"Failed to read config from {config_file}: {e}. Using defaults."
            )
            return DEFAULT_SECURITY_LEVEL_MULTIPLIERS.copy()

    def calculate_score(
        self,
        base_score: float,
        max_score: Optional[float] = None,
        previous_score: Optional[float] = None,
    ) -> float:
        """
        Calculate the adjusted score based on the security level.

        Args:
            base_score (float): The base score before adjustment.
            max_score (Optional[float]): Maximum score cap. If None, no cap is applied.
            previous_score (Optional[float]): Previous score for historical comparison.

        Returns:
            float: The adjusted score based on security level.

        Raises:
            ValueError: If base_score is negative.
        """
        if base_score < 0:
            raise ValueError("base_score must be non-negative")

        # Get multiplier, default to 1.0 if security level is unknown
        multiplier = self.multipliers.get(self.security_level, 1.0)

        # Log warning for unknown security levels
        if self.security_level not in self.multipliers:
            logger.warning(
                f"Unknown security level {self.security_level}. Using default multiplier of 1.0"
            )

        adjusted_score = base_score * multiplier

        # Apply max score cap if specified
        if max_score is not None and adjusted_score > max_score:
            adjusted_score = max_score

        # Create audit trail entry with historical comparison if provided
        points_change = adjusted_score - base_score
        reason = f"{self.security_level.value.upper()} security level multiplier"

        if previous_score is not None:
            historical_delta = adjusted_score - previous_score
            if historical_delta > 0:
                reason += f" (Score increased by {abs(historical_delta):.1f} compared to last run)"
            elif historical_delta < 0:
                reason += f" (Score decreased by {abs(historical_delta):.1f} compared to last run)"
            else:
                reason += " (Score unchanged from last run)"

        audit_entry = AuditEntry(
            reason=reason,
            points=f"{points_change:+.1f} ({multiplier}x applied)",
            security_level=self.security_level.value,
            original_score=base_score,
            adjusted_score=adjusted_score,
            previous_score=previous_score,
        )
        self.audit_trail.append(audit_entry)

        return adjusted_score

    def get_audit_trail(
        self, detail_level: Literal["summary", "full"] = "full"
    ) -> List[Dict]:
        """
        Get the audit trail of all scoring operations.

        Args:
            detail_level (Literal["summary", "full"]): Level of detail to return.
                - "summary": Returns only reason and adjusted_score
                - "full": Returns all fields including timestamps and historical data

        Returns:
            List[Dict]: List of audit entries as dictionaries.
        """
        return [entry.to_dict(detail_level=detail_level) for entry in self.audit_trail]

    def clear_audit_trail(self) -> None:
        """Clear the audit trail."""
        self.audit_trail.clear()

    def export_audit_trail_json(
        self, filepath: str, detail_level: Literal["summary", "full"] = "full"
    ) -> None:
        """
        Export audit trail to a JSON file.

        Args:
            filepath (str): Path to the output JSON file.
            detail_level (Literal["summary", "full"]): Level of detail to export.
        """
        audit_data = {
            "security_level": self.security_level.value,
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "entries": self.get_audit_trail(detail_level=detail_level),
        }

        with open(filepath, "w") as f:
            json.dump(audit_data, f, indent=2)

        logger.info(f"Exported {len(self.audit_trail)} audit entries to {filepath}")

    def export_audit_trail_csv(self, filepath: str) -> None:
        """
        Export audit trail to a CSV file.

        Args:
            filepath (str): Path to the output CSV file.
        """
        if not self.audit_trail:
            logger.warning("No audit trail entries to export")
            return

        fieldnames = [
            "timestamp",
            "reason",
            "points",
            "security_level",
            "original_score",
            "adjusted_score",
            "previous_score",
            "historical_delta",
        ]

        with open(filepath, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for entry in self.audit_trail:
                row = entry.to_dict(detail_level="full")
                # Add missing fields with defaults
                row.setdefault("historical_delta", None)
                row.setdefault("previous_score", None)
                writer.writerow(row)

        logger.info(f"Exported {len(self.audit_trail)} audit entries to {filepath}")
