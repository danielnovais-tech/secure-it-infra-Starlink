# Changelog

All notable changes to the Security Scoring System will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-15

### Added

#### Core Features
- **SecurityLevel Enum** - Three security levels: CRITICAL (0.7x), ELEVATED (0.9x), NORMAL (1.0x)
- **SecurityScorer Class** - Main scoring engine with configurable multipliers
- **Dictionary-based multiplier lookup** - Maintainable and extensible score adjustments

#### Configuration & Validation
- **JSON configuration file support** - External config files for deployment-specific settings
- **Config schema validation** - `validate_config_schema()` function with comprehensive checks
- **ConfigValidationError exception** - Clear error reporting for misconfiguration
- **Custom multiplier overrides** - Direct dictionary parameter for runtime customization
- **Non-negative multiplier validation** - Prevents negative multipliers
- **Unusual value warnings** - Warns when multipliers exceed 2.0

#### Audit Trail System
- **AuditEntry class** - Structured audit logging
- **ISO timestamp tracking** - Precise timing for each scoring operation
- **Historical comparison tracking** - `previous_score` parameter for delta calculations
- **Narrative descriptions** - Human-readable change descriptions
- **Configurable verbosity levels** - Summary vs full detail modes
- **JSON export** - `export_audit_trail_json()` with metadata and timestamps
- **CSV export** - `export_audit_trail_csv()` for dashboard integration
- **Audit trail management** - `get_audit_trail()` and `clear_audit_trail()` methods

#### Robustness & Error Handling
- **Input validation** - Prevents negative base scores
- **Graceful unknown level handling** - Defaults to 1.0x multiplier with warning logging
- **Optional max score capping** - `max_score` parameter for boundary enforcement
- **Boundary case handling** - Proper handling of zero scores and very high scores

#### Testing & Quality
- **34 comprehensive unit tests** - Covering all features and edge cases
- **TestConfigValidation class** - 5 tests for schema validation
- **TestIntegration class** - 2 end-to-end workflow tests
- **CodeQL security scanning** - 0 vulnerabilities detected
- **Python 3.12+ compatibility** - Uses `datetime.now(timezone.utc)` instead of deprecated `utcnow()`

#### Documentation & Examples
- **Comprehensive README** - Complete API reference and usage examples
- **8 example scenarios** - `example.py` demonstrating all features
- **Sample config file** - `config.json` with validation examples
- **Inline code documentation** - Docstrings for all public methods
- **Type hints** - Full typing support for better IDE integration

### Changed
- Refactored score calculation from if-elif chains to dictionary lookup
- Improved CSV export using `setdefault()` for cleaner code
- Enhanced audit trail to support both summary and full detail levels

### Fixed
- Replaced deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)`
- Improved error handling for config file loading

### Security
- CodeQL security scan: 0 vulnerabilities
- Input validation prevents negative scores
- Schema validation prevents misconfigured multipliers
- Comprehensive error handling throughout

## [0.1.0] - 2026-01-06 (Initial Commit)

### Added
- Repository initialization
- Basic project structure
- License (Apache 2.0)
- .gitignore for Python projects

---

**Note**: Version 1.0.0 represents the first production-ready release with complete feature set, comprehensive testing, and documentation.
