from setuptools import setup, find_packages

setup(
    name="wave-guide",
    version="0.1.0",
    packages=find_packages(exclude=["tests*"]),
    install_requires=[
        # List your project dependencies here
        # e.g., "requests>=2.25.1",
    ],
    python_requires=">=3.7",
) 