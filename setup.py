from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="salesforce-metadata-parser",
    version="0.1.0",
    author="Carlos Augusto Osuna",
    author_email="carlososuna86@gmail.com",
    description="A Python CLI tool for parsing Salesforce metadata files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/carlososuna86/salesforce-metadata-parser",
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
            "salesforce-metadata-parser=salesforce_metadata_parser.cli.main:cli",
        ],
    },
)
