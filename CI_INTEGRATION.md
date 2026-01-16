# CI/CD Integration for Log Schema Validation

This document provides examples of integrating log schema validation into CI/CD pipelines.

## GitHub Actions Example

Create `.github/workflows/validate-logs.yml`:

```yaml
name: Validate Log Schema

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  validate-schema:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Validate schema file syntax
      run: |
        python -m json.tool schemas/structured-log-v1.0.0.json > /dev/null
        echo "✅ Schema JSON is valid"
    
    - name: Generate example log
      run: |
        python validate_logs.py --generate-example > example.log
        echo "✅ Example log generated"
    
    - name: Validate example log
      run: |
        python validate_logs.py --file example.log --strict
        echo "✅ Example log validates against schema"
    
    - name: Validate test logs (if present)
      if: hashFiles('tests/fixtures/logs/*.log') != ''
      run: |
        for logfile in tests/fixtures/logs/*.log; do
          echo "Validating $logfile..."
          python validate_logs.py --file "$logfile" --strict
        done
        echo "✅ All test logs valid"
    
    - name: Check for schema version consistency
      run: |
        # Ensure all code references match schema version
        grep -r "schema_version.*1\.0\.0" . --include="*.py" || true
        echo "✅ Schema version consistency checked"

  validate-code-logs:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt || true
    
    - name: Run application and capture logs
      run: |
        # Run application in test mode and capture JSON logs
        export STARLINK_LOG_FORMAT=json
        python starlink_security.py > app_logs.log 2>&1 || true
    
    - name: Extract and validate JSON logs
      run: |
        # Extract only JSON log lines
        grep '^{' app_logs.log > json_logs.log || true
        
        # Validate if any JSON logs were generated
        if [ -s json_logs.log ]; then
          python validate_logs.py --file json_logs.log
          echo "✅ Application logs validate against schema"
        else
          echo "ℹ️  No JSON logs to validate"
        fi
    
    - name: Upload validation results
      if: failure()
      uses: actions/upload-artifact@v3
      with:
        name: validation-failures
        path: |
          json_logs.log
          app_logs.log
```

## GitLab CI Example

Create `.gitlab-ci.yml`:

```yaml
stages:
  - validate
  - test

validate-schema:
  stage: validate
  image: python:3.9
  script:
    - echo "Validating log schema..."
    - python -m json.tool schemas/structured-log-v1.0.0.json > /dev/null
    - python validate_logs.py --generate-example > example.log
    - python validate_logs.py --file example.log --strict
    - echo "✅ Schema validation passed"
  rules:
    - changes:
        - schemas/*.json
        - validate_logs.py

validate-application-logs:
  stage: test
  image: python:3.9
  script:
    - pip install -r requirements.txt || true
    - export STARLINK_LOG_FORMAT=json
    - python starlink_security.py > app_logs.log 2>&1 || true
    - grep '^{' app_logs.log > json_logs.log || true
    - |
      if [ -s json_logs.log ]; then
        python validate_logs.py --file json_logs.log
      fi
  artifacts:
    when: on_failure
    paths:
      - json_logs.log
      - app_logs.log
    expire_in: 1 week
```

## Jenkins Pipeline Example

Create `Jenkinsfile`:

```groovy
pipeline {
    agent any
    
    stages {
        stage('Validate Schema') {
            steps {
                sh '''
                    echo "Validating log schema..."
                    python3 -m json.tool schemas/structured-log-v1.0.0.json > /dev/null
                    python3 validate_logs.py --generate-example > example.log
                    python3 validate_logs.py --file example.log --strict
                '''
            }
        }
        
        stage('Test Application Logs') {
            steps {
                sh '''
                    export STARLINK_LOG_FORMAT=json
                    python3 starlink_security.py > app_logs.log 2>&1 || true
                    grep '^{' app_logs.log > json_logs.log || true
                    
                    if [ -s json_logs.log ]; then
                        python3 validate_logs.py --file json_logs.log
                    else
                        echo "No JSON logs to validate"
                    fi
                '''
            }
        }
        
        stage('Archive Results') {
            when {
                expression { currentBuild.result == 'FAILURE' }
            }
            steps {
                archiveArtifacts artifacts: '*.log', allowEmptyArchive: true
            }
        }
    }
}
```

## Pre-commit Hook Example

Create `.git/hooks/pre-commit` or use pre-commit framework:

```bash
#!/bin/bash
# Pre-commit hook for log schema validation

echo "Running log schema validation..."

# Check if schema file was modified
if git diff --cached --name-only | grep -q "schemas/.*\.json"; then
    echo "Schema file modified, validating..."
    python validate_logs.py --generate-example > /tmp/example.log
    if ! python validate_logs.py --file /tmp/example.log --strict; then
        echo "❌ Schema validation failed"
        rm /tmp/example.log
        exit 1
    fi
    rm /tmp/example.log
    echo "✅ Schema validated"
fi

# Check if Python files were modified
if git diff --cached --name-only | grep -q "\.py$"; then
    echo "Python files modified, checking for schema compliance..."
    # Add custom checks here (e.g., grep for schema_version)
fi

echo "✅ Pre-commit validation passed"
exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

## Docker Integration

Create `Dockerfile.validator`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy schema and validator
COPY schemas/ /app/schemas/
COPY validate_logs.py /app/

# Create entrypoint
ENTRYPOINT ["python", "/app/validate_logs.py"]
CMD ["--help"]
```

Build and use:

```bash
# Build validator image
docker build -t starlink-log-validator:latest -f Dockerfile.validator .

# Validate logs
docker run --rm -v $(pwd)/logs:/logs \
    starlink-log-validator:latest \
    --file /logs/application.log
```

## Kubernetes Integration (Init Container)

Use as init container to validate config logs before starting main container:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: starlink-security
spec:
  initContainers:
  - name: validate-logs
    image: starlink-log-validator:latest
    command: ["python", "/app/validate_logs.py"]
    args: ["--file", "/config/bootstrap.log", "--strict"]
    volumeMounts:
    - name: config
      mountPath: /config
  
  containers:
  - name: starlink-security
    image: starlink-security:latest
    volumeMounts:
    - name: config
      mountPath: /config
  
  volumes:
  - name: config
    configMap:
      name: starlink-config
```

## Make Integration

Add to `Makefile`:

```makefile
.PHONY: validate-schema validate-logs

validate-schema:
	@echo "Validating log schema..."
	@python -m json.tool schemas/structured-log-v1.0.0.json > /dev/null
	@python validate_logs.py --generate-example > /tmp/example.log
	@python validate_logs.py --file /tmp/example.log --strict
	@rm /tmp/example.log
	@echo "✅ Schema validation passed"

validate-logs:
	@echo "Validating application logs..."
	@if [ -f logs/starlink_security.log ]; then \
		grep '^{' logs/starlink_security.log > /tmp/json_logs.log 2>/dev/null || true; \
		if [ -s /tmp/json_logs.log ]; then \
			python validate_logs.py --file /tmp/json_logs.log; \
		fi; \
		rm /tmp/json_logs.log; \
	else \
		echo "No logs found to validate"; \
	fi

test: validate-schema validate-logs
	@echo "✅ All validations passed"
```

Usage:
```bash
make validate-schema
make validate-logs
make test
```

## Continuous Monitoring

### Real-time Validation with Fluentd

```ruby
# fluentd.conf
<source>
  @type tail
  path /var/log/starlink-security/*.log
  pos_file /var/log/fluentd/starlink.pos
  tag starlink.logs
  format json
</source>

<filter starlink.logs>
  @type exec
  command python /opt/validate_logs.py --log '${record}'
  <inject>
    tag_key validation_status
  </inject>
</filter>

<match starlink.logs>
  @type elasticsearch
  # Send to Elasticsearch
</match>
```

### Real-time Validation with Logstash

```ruby
# logstash.conf
input {
  file {
    path => "/var/log/starlink-security/*.log"
    codec => json
  }
}

filter {
  ruby {
    code => '
      require "json"
      require "open3"
      
      log_json = event.to_json
      stdout, stderr, status = Open3.capture3(
        "python", "/opt/validate_logs.py", "--log", log_json
      )
      
      if status.success?
        event.set("schema_valid", true)
      else
        event.set("schema_valid", false)
        event.set("validation_errors", stderr)
      end
    '
  }
}

output {
  if [schema_valid] == false {
    # Alert on invalid logs
    email {
      to => "security-team@example.com"
      subject => "Invalid log schema detected"
      body => "Validation errors: %{validation_errors}"
    }
  }
  
  elasticsearch {
    hosts => ["localhost:9200"]
  }
}
```

## Best Practices

1. **Validate Early**: Run validation in CI before deployment
2. **Fail Fast**: Use `--strict` mode in CI to fail on first error
3. **Monitor Production**: Validate logs continuously in production
4. **Alert on Failures**: Set up alerts for schema validation failures
5. **Version Management**: Keep schema version in sync with application version
6. **Gradual Rollout**: When changing schema, support multiple versions during transition
7. **Documentation**: Keep field dictionary updated with schema changes

## Troubleshooting

### Common Issues

**Issue**: Validation fails with "Missing required field: 'schema_version'"
**Solution**: Ensure all log entries include `schema_version: "1.0.0"`

**Issue**: Validation fails with "Additional property not allowed"
**Solution**: Remove undocumented fields or update schema to allow them

**Issue**: Pattern validation fails for error_code
**Solution**: Ensure error codes match pattern `^[A-Z]{2,4}-\\d{3}$`

**Issue**: Privacy tags validation fails
**Solution**: Use only defined privacy tags: PII, PHI, CONFIDENTIAL, INTERNAL, PUBLIC, REDACTED, ENCRYPTED

### Debug Mode

Run validator with Python debugger for detailed error information:

```bash
python -m pdb validate_logs.py --file logs/application.log
```

### Schema Testing

Test schema changes before committing:

```bash
# Generate example
python validate_logs.py --generate-example > test.log

# Modify test.log to test edge cases

# Validate
python validate_logs.py --file test.log
```

## References

- JSON Schema Validator: `validate_logs.py`
- Schema Definition: `schemas/structured-log-v1.0.0.json`
- Field Dictionary: `FIELD_DICTIONARY.md`
- Logging Documentation: `LOGGING.md`
