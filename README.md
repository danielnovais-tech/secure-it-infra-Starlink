# secure-it-infra-Starlink
Repository dedicated to security solutions for managed enterprise infrastructures supporting Starlink.

## Usage Examples

### Run comprehensive audit
```bash
python secure_it_infra.py --audit --config config.json
```

### Generate audit with recommendations
```bash
python secure_it_infra.py --audit --recommendations
```

### Check specific security domains
```bash
python secure_it_infra.py --check-network --check-encryption
```

### Save report to file
```bash
python secure_it_infra.py --audit --output security_report.json
```
