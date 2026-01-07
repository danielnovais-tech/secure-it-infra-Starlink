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
    },
)
