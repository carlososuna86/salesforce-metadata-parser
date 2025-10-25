from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="salesforce-metadata-parser",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A Python CLI tool for parsing Salesforce metadata files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/salesforce-metadata-parser",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        # Add your dependencies here
    ],
    entry_points={
        "console_scripts": [
            "salesforce-metadata-parser=salesforce_metadata_parser.main:main",
        ],
    },
)
