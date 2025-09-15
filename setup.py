#!/usr/bin/env python3
"""Setup script for the model scoring package."""

from setuptools import setup, find_packages

setup(
    name="model-scorer",
    version="1.0.0",
    author="Anjali Vanamala, Andrew Diab, Pryce Tharpe, Shaantanu Sriram",
    description="A tool for scoring and evaluating machine learning models",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    entry_points={
        "console_scripts": [
            "model-scorer=src.main:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
