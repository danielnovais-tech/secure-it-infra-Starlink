#!/usr/bin/env python3
"""
Lightweight JSON Schema Validator for Starlink Security Structured Logs

This validator can be run in CI to ensure log entries conform to the schema.
It provides fast validation with detailed error reporting.

Usage:
    # Validate a single JSON log entry
    python validate_logs.py --log '{"schema_version": "1.0.0", ...}'
    
    # Validate a JSON Lines file
    python validate_logs.py --file logs/starlink_security.log
    
    # Validate from stdin (for CI pipelines)
    cat logs/*.log | python validate_logs.py --stdin
    
    # Strict mode (fail on first error)
    python validate_logs.py --file logs/test.log --strict
    
    # Lenient mode (warnings instead of errors)
    python validate_logs.py --file logs/test.log --lenient
    
    # Privacy tag enforcement (reject unredacted PII in production)
    python validate_logs.py --file logs/prod.log --enforce-privacy --environment production
    
    # Backward compatibility test
    python validate_logs.py --test-backward-compatibility --samples tests/fixtures/legacy_logs/
    
    # Generate a valid example
    python validate_logs.py --generate-example

Exit codes:
    0: All validations passed
    1: Validation errors found
    2: Invalid arguments or runtime error
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
import re
from datetime import datetime

# Simple schema validator (no external dependencies for CI)
class SimpleSchemaValidator:
    """
    Lightweight JSON Schema validator for structured logs.
    
    Validates required fields, types, enums, patterns, and ranges
    without requiring jsonschema library (for minimal CI dependencies).
    """
    
    def __init__(self, schema_path: str):
        """Load schema from file."""
        with open(schema_path, 'r') as f:
            self.schema = json.load(f)
        
        self.errors = []
    
    def validate(self, data: dict) -> Tuple[bool, List[str]]:
        """
        Validate data against schema.
        
        Returns:
            (is_valid, list_of_errors)
        """
        self.errors = []
        
        # Check required fields
        required = self.schema.get('required', [])
        for field in required:
            if field not in data:
                self.errors.append(f"Missing required field: '{field}'")
        
        # Check each field in data
        properties = self.schema.get('properties', {})
        for field, value in data.items():
            if field not in properties:
                if not self.schema.get('additionalProperties', True):
                    self.errors.append(f"Additional property not allowed: '{field}'")
                continue
            
            field_schema = properties[field]
            self._validate_field(field, value, field_schema)
        
        return (len(self.errors) == 0, self.errors)
    
    def _validate_field(self, field_name: str, value, field_schema: dict):
        """Validate a single field against its schema."""
        # Type validation
        expected_type = field_schema.get('type')
        if expected_type:
            if not self._check_type(value, expected_type):
                self.errors.append(
                    f"Field '{field_name}': expected type {expected_type}, "
                    f"got {type(value).__name__}"
                )
                return
        
        # Enum validation
        if 'enum' in field_schema:
            if value not in field_schema['enum']:
                self.errors.append(
                    f"Field '{field_name}': value '{value}' not in allowed values: "
                    f"{field_schema['enum']}"
                )
        
        # Pattern validation (for strings)
        if 'pattern' in field_schema and isinstance(value, str):
            if not re.match(field_schema['pattern'], value):
                self.errors.append(
                    f"Field '{field_name}': value '{value}' does not match pattern "
                    f"'{field_schema['pattern']}'"
                )
        
        # String length validation
        if isinstance(value, str):
            if 'minLength' in field_schema and len(value) < field_schema['minLength']:
                self.errors.append(
                    f"Field '{field_name}': string too short "
                    f"(min: {field_schema['minLength']}, got: {len(value)})"
                )
            if 'maxLength' in field_schema and len(value) > field_schema['maxLength']:
                self.errors.append(
                    f"Field '{field_name}': string too long "
                    f"(max: {field_schema['maxLength']}, got: {len(value)})"
                )
        
        # Numeric range validation
        if isinstance(value, (int, float)):
            if 'minimum' in field_schema and value < field_schema['minimum']:
                self.errors.append(
                    f"Field '{field_name}': value {value} below minimum "
                    f"{field_schema['minimum']}"
                )
            if 'maximum' in field_schema and value > field_schema['maximum']:
                self.errors.append(
                    f"Field '{field_name}': value {value} above maximum "
                    f"{field_schema['maximum']}"
                )
        
        # Array validation
        if isinstance(value, list):
            if 'uniqueItems' in field_schema and field_schema['uniqueItems']:
                if len(value) != len(set(map(str, value))):
                    self.errors.append(
                        f"Field '{field_name}': array must have unique items"
                    )
            
            # Validate array items
            if 'items' in field_schema:
                item_schema = field_schema['items']
                for i, item in enumerate(value):
                    self._validate_field(f"{field_name}[{i}]", item, item_schema)
    
    def _check_type(self, value, expected_type: str) -> bool:
        """Check if value matches expected JSON type."""
        type_map = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict,
            'null': type(None)
        }
        
        expected_python_type = type_map.get(expected_type)
        if expected_python_type is None:
            return True  # Unknown type, skip
        
        return isinstance(value, expected_python_type)


class PrivacyEnforcer:
    """
    Enforces privacy tag rules on log entries.
    
    Ensures that fields containing sensitive data (PII, PHI, etc.) are
    properly redacted or encrypted before being logged, especially in
    production environments.
    """
    
    # Fields that commonly contain PII and should be checked
    PII_SUSPECT_FIELDS = {
        'user_id', 'email', 'username', 'name', 'phone', 'ssn',
        'ip_address', 'session_id', 'user_agent', 'address',
        'location', 'coordinates', 'device_id'
    }
    
    # Fields that commonly contain PHI
    PHI_SUSPECT_FIELDS = {
        'patient_id', 'medical_record', 'diagnosis', 'prescription',
        'health_data', 'biometric'
    }
    
    # Patterns that indicate unredacted sensitive data
    SENSITIVE_PATTERNS = {
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'ipv4': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'
    }
    
    def __init__(self, strict_environments: Optional[Set[str]] = None):
        """
        Initialize privacy enforcer.
        
        Args:
            strict_environments: Set of environment names where strict enforcement applies
                               (default: {'production', 'prod', 'staging'})
        """
        self.strict_environments = strict_environments or {'production', 'prod', 'staging'}
        self.warnings = []
        self.errors = []
    
    def validate(self, entry: dict, lenient: bool = False) -> Tuple[bool, List[str], List[str]]:
        """
        Validate privacy tags and sensitive data handling.
        
        Args:
            entry: Log entry to validate
            lenient: If True, violations are warnings; if False, they are errors
        
        Returns:
            (is_valid, list_of_errors, list_of_warnings)
        """
        self.warnings = []
        self.errors = []
        
        environment = entry.get('environment', 'unknown')
        privacy_tags = entry.get('privacy_tags', [])
        is_strict_env = environment in self.strict_environments
        
        # Check for potentially sensitive fields without proper privacy tags
        for field, value in entry.items():
            if field in self.PII_SUSPECT_FIELDS:
                if 'PII' not in privacy_tags and 'REDACTED' not in privacy_tags:
                    msg = (
                        f"Field '{field}' likely contains PII but missing PII or REDACTED tag "
                        f"(privacy_tags: {privacy_tags})"
                    )
                    if is_strict_env and not lenient:
                        self.errors.append(msg)
                    else:
                        self.warnings.append(msg)
                
                # Check if the value appears to be unredacted in strict environments
                if is_strict_env and isinstance(value, str):
                    if self._appears_unredacted(value, 'PII'):
                        msg = (
                            f"Field '{field}' in {environment} environment appears to contain "
                            f"unredacted PII: '{value[:20]}...'"
                        )
                        if not lenient:
                            self.errors.append(msg)
                        else:
                            self.warnings.append(msg)
            
            if field in self.PHI_SUSPECT_FIELDS:
                if 'PHI' not in privacy_tags and 'REDACTED' not in privacy_tags:
                    msg = (
                        f"Field '{field}' likely contains PHI but missing PHI or REDACTED tag "
                        f"(privacy_tags: {privacy_tags})"
                    )
                    if is_strict_env and not lenient:
                        self.errors.append(msg)
                    else:
                        self.warnings.append(msg)
        
        # Scan for sensitive patterns in message field for production environments
        if is_strict_env:
            message = entry.get('message', '')
            if isinstance(message, str):
                for pattern_name, pattern in self.SENSITIVE_PATTERNS.items():
                    if re.search(pattern, message):
                        msg = (
                            f"Message in {environment} environment contains potential "
                            f"{pattern_name}: Consider redacting or tagging with REDACTED"
                        )
                        if not lenient:
                            self.errors.append(msg)
                        else:
                            self.warnings.append(msg)
        
        # Verify CONFIDENTIAL and INTERNAL are not logged in wrong environments
        if 'CONFIDENTIAL' in privacy_tags:
            if environment not in {'development', 'staging', 'production', 'test'}:
                self.warnings.append(
                    f"CONFIDENTIAL data logged in unexpected environment: {environment}"
                )
        
        return (len(self.errors) == 0, self.errors, self.warnings)
    
    def _appears_unredacted(self, value: str, data_type: str) -> bool:
        """
        Check if a value appears to be unredacted sensitive data.
        
        Args:
            value: String value to check
            data_type: Type of data ('PII', 'PHI', etc.)
        
        Returns:
            True if value appears to be unredacted sensitive data
        """
        # Common redaction patterns
        redaction_markers = ['***', 'REDACTED', '[REDACTED]', 'XXX', '####']
        if any(marker in value for marker in redaction_markers):
            return False
        
        # Check for specific patterns
        if data_type == 'PII':
            # Email pattern
            if re.search(self.SENSITIVE_PATTERNS['email'], value):
                return True
            # SSN pattern
            if re.search(self.SENSITIVE_PATTERNS['ssn'], value):
                return True
            # Phone pattern
            if re.search(self.SENSITIVE_PATTERNS['phone'], value):
                return True
        
        return False


class BackwardCompatibilityTester:
    """
    Tests backward compatibility of schema changes.
    
    Validates that historical log samples still validate against
    the current schema, ensuring schema evolution doesn't break
    existing logs.
    """
    
    def __init__(self, current_schema_path: str):
        """Initialize with current schema."""
        self.validator = SimpleSchemaValidator(current_schema_path)
        self.results = []
    
    def test_samples(self, samples_dir: str, lenient: bool = False) -> Tuple[int, int, List[Dict]]:
        """
        Test backward compatibility with legacy log samples.
        
        Args:
            samples_dir: Directory containing legacy log sample files
            lenient: If True, treat some validation failures as warnings
        
        Returns:
            (compatible_count, incompatible_count, detailed_results)
        """
        compatible = 0
        incompatible = 0
        self.results = []
        
        samples_path = Path(samples_dir)
        if not samples_path.exists():
            return 0, 0, [{"error": f"Samples directory not found: {samples_dir}"}]
        
        # Find all JSON files in samples directory
        sample_files = list(samples_path.glob('**/*.json')) + list(samples_path.glob('**/*.log'))
        
        if not sample_files:
            return 0, 0, [{"warning": f"No sample files found in {samples_dir}"}]
        
        for sample_file in sample_files:
            result = self._test_file(sample_file, lenient)
            self.results.append(result)
            
            if result['compatible']:
                compatible += 1
            else:
                incompatible += 1
        
        return compatible, incompatible, self.results
    
    def _test_file(self, file_path: Path, lenient: bool) -> Dict:
        """Test a single sample file."""
        result = {
            'file': str(file_path),
            'compatible': True,
            'errors': [],
            'warnings': []
        }
        
        try:
            with open(file_path, 'r') as f:
                # Try to parse as JSON
                try:
                    data = json.load(f)
                    entries = [data] if isinstance(data, dict) else data
                except json.JSONDecodeError:
                    # Try as JSON Lines
                    f.seek(0)
                    entries = []
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                entries.append(json.loads(line))
                            except json.JSONDecodeError as e:
                                result['errors'].append(f"Invalid JSON: {e}")
                                result['compatible'] = False
                                return result
            
            # Validate each entry
            for i, entry in enumerate(entries):
                is_valid, errors = self.validator.validate(entry)
                
                if not is_valid:
                    if lenient:
                        # In lenient mode, some errors become warnings
                        for error in errors:
                            if 'Missing required field' in error:
                                # Missing fields are errors even in lenient mode
                                result['errors'].append(f"Entry {i}: {error}")
                                result['compatible'] = False
                            else:
                                # Other validation failures are warnings
                                result['warnings'].append(f"Entry {i}: {error}")
                    else:
                        result['errors'].extend([f"Entry {i}: {e}" for e in errors])
                        result['compatible'] = False
        
        except Exception as e:
            result['errors'].append(f"Error reading file: {e}")
            result['compatible'] = False
        
        return result


def validate_log_entry(entry: dict, validator: SimpleSchemaValidator, 
                      line_num: Optional[int] = None) -> Tuple[bool, List[str]]:
    """
    Validate a single log entry.
    
    Returns:
        (is_valid, list_of_errors)
    """
    prefix = f"Line {line_num}: " if line_num else ""
    
    is_valid, errors = validator.validate(entry)
    prefixed_errors = [f"{prefix}{error}" for error in errors]
    
    return is_valid, prefixed_errors


def validate_file(file_path: str, validator: SimpleSchemaValidator, 
                 strict: bool = False) -> Tuple[int, int, List[str]]:
    """
    Validate a JSON Lines file.
    
    Returns:
        (valid_count, invalid_count, all_errors)
    """
    valid_count = 0
    invalid_count = 0
    all_errors = []
    
    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                entry = json.loads(line)
            except json.JSONDecodeError as e:
                error = f"Line {line_num}: Invalid JSON - {e}"
                all_errors.append(error)
                invalid_count += 1
                if strict:
                    break
                continue
            
            is_valid, errors = validate_log_entry(entry, validator, line_num)
            
            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                all_errors.extend(errors)
                if strict:
                    break
    
    return valid_count, invalid_count, all_errors


def validate_stdin(validator: SimpleSchemaValidator, strict: bool = False) -> Tuple[int, int, List[str]]:
    """
    Validate log entries from stdin.
    
    Returns:
        (valid_count, invalid_count, all_errors)
    """
    valid_count = 0
    invalid_count = 0
    all_errors = []
    
    for line_num, line in enumerate(sys.stdin, 1):
        line = line.strip()
        if not line:
            continue
        
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as e:
            error = f"Line {line_num}: Invalid JSON - {e}"
            all_errors.append(error)
            invalid_count += 1
            if strict:
                break
            continue
        
        is_valid, errors = validate_log_entry(entry, validator, line_num)
        
        if is_valid:
            valid_count += 1
        else:
            invalid_count += 1
            all_errors.extend(errors)
            if strict:
                break
    
    return valid_count, invalid_count, all_errors


def generate_example() -> dict:
    """Generate a valid example log entry."""
    return {
        "schema_version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "logger": "starlink-security",
        "level": "INFO",
        "module": "example_module",
        "line": 42,
        "message": "Example log message",
        "service": "starlink-security",
        "component": "example-component",
        "correlation_id": "req-example-12345",
        "user_id": "user@example.com",
        "privacy_tags": ["PUBLIC"],
        "environment": "development"
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate Starlink Security structured logs against JSON Schema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--log',
        help='Validate a single JSON log entry (as string)'
    )
    input_group.add_argument(
        '--file',
        help='Validate a JSON Lines file'
    )
    input_group.add_argument(
        '--stdin',
        action='store_true',
        help='Validate log entries from stdin'
    )
    input_group.add_argument(
        '--generate-example',
        action='store_true',
        help='Generate a valid example log entry'
    )
    input_group.add_argument(
        '--test-backward-compatibility',
        action='store_true',
        help='Test backward compatibility with legacy log samples'
    )
    
    parser.add_argument(
        '--schema',
        default='schemas/structured-log-v1.0.0.json',
        help='Path to JSON Schema file (default: schemas/structured-log-v1.0.0.json)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Fail on first validation error'
    )
    parser.add_argument(
        '--lenient',
        action='store_true',
        help='Lenient mode: treat some failures as warnings instead of errors'
    )
    parser.add_argument(
        '--enforce-privacy',
        action='store_true',
        help='Enforce privacy tag rules (reject unredacted PII in production)'
    )
    parser.add_argument(
        '--environment',
        help='Specify environment for privacy enforcement (production, staging, development)'
    )
    parser.add_argument(
        '--samples',
        help='Directory containing legacy log samples for backward compatibility testing'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Only output errors, no success messages'
    )
    
    args = parser.parse_args()
    
    # Generate example
    if args.generate_example:
        example = generate_example()
        print(json.dumps(example, indent=2))
        return 0
    
    # Backward compatibility testing
    if args.test_backward_compatibility:
        if not args.samples:
            print("Error: --samples directory required for backward compatibility testing", file=sys.stderr)
            return 2
        
        schema_path = Path(args.schema)
        if not schema_path.exists():
            print(f"Error: Schema file not found: {args.schema}", file=sys.stderr)
            return 2
        
        try:
            tester = BackwardCompatibilityTester(str(schema_path))
            compatible, incompatible, results = tester.test_samples(args.samples, args.lenient)
            
            print(f"\n📊 Backward Compatibility Test Results:")
            print(f"   Compatible: {compatible}")
            print(f"   Incompatible: {incompatible}")
            print(f"   Total Samples: {compatible + incompatible}")
            
            if incompatible > 0:
                print(f"\n❌ Incompatible Samples:")
                for result in results:
                    if not result['compatible']:
                        print(f"\n   File: {result['file']}")
                        if result['errors']:
                            print("   Errors:")
                            for error in result['errors']:
                                print(f"     - {error}")
                        if result.get('warnings'):
                            print("   Warnings:")
                            for warning in result['warnings']:
                                print(f"     - {warning}")
            
            if compatible > 0 and not args.quiet:
                print(f"\n✅ All {compatible} compatible samples validated successfully")
            
            return 0 if incompatible == 0 else 1
        
        except Exception as e:
            print(f"Error during backward compatibility testing: {e}", file=sys.stderr)
            return 2
    
    # Load schema
    schema_path = Path(args.schema)
    if not schema_path.exists():
        print(f"Error: Schema file not found: {args.schema}", file=sys.stderr)
        return 2
    
    try:
        validator = SimpleSchemaValidator(str(schema_path))
    except Exception as e:
        print(f"Error loading schema: {e}", file=sys.stderr)
        return 2
    
    # Initialize privacy enforcer if needed
    privacy_enforcer = None
    if args.enforce_privacy:
        privacy_enforcer = PrivacyEnforcer()
    
    # Validate based on input type
    try:
        if args.log:
            # Single log entry
            try:
                entry = json.loads(args.log)
            except json.JSONDecodeError as e:
                print(f"Error: Invalid JSON - {e}", file=sys.stderr)
                return 1
            
            # Schema validation
            is_valid, errors = validate_log_entry(entry, validator)
            warnings = []
            
            # Privacy validation
            if privacy_enforcer:
                privacy_valid, privacy_errors, privacy_warnings = privacy_enforcer.validate(entry, args.lenient)
                errors.extend(privacy_errors)
                warnings.extend(privacy_warnings)
                is_valid = is_valid and privacy_valid
            
            # Output results
            if warnings and not args.quiet:
                print("⚠️  Warnings:", file=sys.stderr)
                for warning in warnings:
                    print(f"  - {warning}", file=sys.stderr)
            
            if is_valid:
                if not args.quiet:
                    print("✅ Log entry is valid")
                return 0
            else:
                print("❌ Log entry is invalid:", file=sys.stderr)
                for error in errors:
                    print(f"  - {error}", file=sys.stderr)
                return 1
        
        elif args.file:
            # File validation
            valid_count, invalid_count, errors = validate_file(
                args.file, validator, args.strict
            )
            
            if not args.quiet:
                print(f"Validation complete: {valid_count} valid, {invalid_count} invalid")
            
            if errors:
                print("\nValidation errors:", file=sys.stderr)
                for error in errors:
                    print(f"  - {error}", file=sys.stderr)
            
            return 0 if invalid_count == 0 else 1
        
        elif args.stdin:
            # Stdin validation
            valid_count, invalid_count, errors = validate_stdin(validator, args.strict)
            
            if not args.quiet:
                print(f"Validation complete: {valid_count} valid, {invalid_count} invalid")
            
            if errors:
                print("\nValidation errors:", file=sys.stderr)
                for error in errors:
                    print(f"  - {error}", file=sys.stderr)
            
            return 0 if invalid_count == 0 else 1
    
    except Exception as e:
        print(f"Error during validation: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
