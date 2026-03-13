"""
Yoimiya SDK - Python Package Setup
"""

from setuptools import setup, find_packages

with open("../../README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="yoimiya-sdk",
    version="0.1.0",
    author="Atlas Protocol",
    author_email="atlasw231@gmail.com",
    description="Yoimiya ZK Proving SDK — universal circuit prover with KZG commitments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/atlasw231-maker/yoimiya-sdk",
    py_modules=["yoimiya"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Business Source License 1.1",
        "Operating System :: OS Independent",
        "Topic :: Security :: Cryptography",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.8",
    keywords="zk zero-knowledge prover bn254 kzg cryptography",
)
