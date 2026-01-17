"""
Minimal smoke tests for recently edited modules.
Run with: python smoke_test.py
"""

import subprocess
import sys


def run_cli(module, args=None):
    """Run a module as a script with optional args."""
    cmd = [sys.executable, module]
    if args:
        cmd.extend(args)
    print(f"\n>>> Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0:
        print(f"ERROR (exit code {result.returncode}):")
        if result.stderr:
            print(result.stderr)
        else:
            print("(no stderr)")


def import_test(module_name):
    """Try importing a module to confirm no syntax/runtime errors."""
    print(f"\n>>> Importing {module_name}")
    try:
        __import__(module_name)
        print("Import OK")
    except Exception as e:
        print("Import FAILED:", e)


if __name__ == "__main__":
    # Modules you touched
    modules = [
        "policy_impact_analyzer",
        "auditor_portal",
        "policy_manager",
    ]

    # Import checks
    for m in modules:
        import_test(m)

    # CLI smoke runs
    run_cli("policy_impact_analyzer.py", ["--help"])
    run_cli("auditor_portal.py", ["--help"])
    run_cli("policy_manager.py", ["--help"])
