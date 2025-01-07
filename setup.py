# setup.py

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cp2k2deepmd", 
    version="0.1.0",  
    author="KemingZhu", 
    author_email="zhukeming0127@gmail.com",
    description="A converter from CP2K output to DeepMD format",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZKMGitHub/cp2k2deepmd",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.18.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
