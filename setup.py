"""Setup configuration for Starlink Security Foundation."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="starlink-security",
    version="0.1.0",
    author="Starlink Security Team",
    description="Security solutions for managed enterprise infrastructures supporting Starlink",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/danielnovais-tech/secure-it-infra-Starlink",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=41.0.0",
        "PyYAML>=6.0.0",
    ],
    entry_points={
        "console_scripts": [
            "starlink-security=starlink_security.foundation:main",
        ],
    },
)
