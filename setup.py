"""Install script: lets `pip install .` turn this folder into an importable package."""

from setuptools import find_packages, setup

setup(
    name="czi_basics",               # same name as the package folder
    version="0.1.0",
    description="Load Zeiss .czi microscopy files and save channels as PNG/TIFF",
    author="Evalds",
    packages=find_packages(exclude=["tests"]),   # finds the czi_basics/ folder
    python_requires=">=3.9",
    # Packages pip installs automatically together with czi_basics.
    install_requires=[
        "numpy",
        "pillow",
        "bioio",       # general microscopy file reader
        "bioio-czi",   # plugin that lets bioio read Zeiss .czi files
    ],
)
