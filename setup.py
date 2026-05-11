"""Roobie — Autonomous Local-First AI Web Developer."""

from setuptools import setup, find_packages

setup(
    name="roobie",
    version="0.1.0",
    description="Autonomous Local-First AI Web Developer CLI",
    long_description=open("readme.md").read(),
    long_description_content_type="text/markdown",
    author="Roobie Team",
    license="MIT",
    python_requires=">=3.9",
    packages=find_packages(),
    install_requires=[
        "typer>=0.9.0",
        "rich>=13.7.0",
        "requests>=2.31.0",
        "psutil>=5.9.0",
    ],
    extras_require={
        "full": [
            "chromadb>=0.4.22",
            "playwright>=1.41.0",
            "crawl4ai>=0.2.0",
            "langgraph>=0.0.40",
        ],
        "llama": [
            "llama-cpp-python>=0.2.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "roobie=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Code Generators",
    ],
)
