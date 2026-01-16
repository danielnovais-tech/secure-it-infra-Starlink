"""Setup configuration for secure-it-infra-Starlink."""
from setuptools import setup, find_packages

setup(
    name="secure-it-infra-starlink",
    version="0.1.0",
    description="Security solutions for managed enterprise infrastructures supporting Starlink",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
        ]
"""Setup configuration for secure-it-infra-starlink package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="starlink-metrics",
    version="1.0.0",
    author="Starlink Metrics Team",
    author_email="metrics@example.com",
    description="Comprehensive connection metrics monitoring for Starlink satellite internet",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/danielnovais-tech/secure-it-infra-Starlink",
    project_urls={
        "Bug Tracker": "https://github.com/danielnovais-tech/secure-it-infra-Starlink/issues",
        "Documentation": "https://github.com/danielnovais-tech/secure-it-infra-Starlink/blob/main/README.md",
        "Source Code": "https://github.com/danielnovais-tech/secure-it-infra-Starlink",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Telecommunications Industry",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Networking :: Monitoring",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    name="secure-it-infra-starlink",
    version="0.1.0",
    author="Secure IT Infra",
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
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    py_modules=["starlink_metrics", "observability"],
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies for core functionality
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=41.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
            "isort>=5.10.0",
        ],
        "aws": [
            "boto3>=1.26.0",
        ],
    },
    keywords="starlink metrics monitoring network satellite prometheus cloudwatch observability",
            "pytest-asyncio>=0.21.0",
        ],
    },
)
