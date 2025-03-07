from setuptools import setup, find_packages

setup(
    name="shopping-list-organizer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "rich==13.7.0",
        "typer==0.9.0",
        "python-dotenv==1.0.0",
        "openai==1.12.0",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "shopping-list=src.main:main",
        ],
    },
) 