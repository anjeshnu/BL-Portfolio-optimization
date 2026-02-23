"""
Black-Litterman Portfolio Optimization
A comprehensive implementation of the Black-Litterman model with factor models.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="black-litterman-portfolio",
    version="1.0.0",
    author="Anjeshnu Trivedi",
    author_email="anjeshnu25@gmail.com",
    description="Black-Litterman portfolio optimization with factor models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anjeshnu/black-litterman-portfolio",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bl-optimize=src.cli:main",
        ],
    },
    keywords="portfolio optimization black-litterman factor-models quantitative-finance",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/black-litterman-portfolio/issues",
        "Source": "https://github.com/yourusername/black-litterman-portfolio",
        "Documentation": "https://github.com/yourusername/black-litterman-portfolio/docs",
    },
)
