from setuptools import setup, find_packages

setup(
    name="wave_guide",
    version="0.1",
    packages=find_packages(include=['wave_guide', 'wave_guide.*']),
    install_requires=[
        "flask==2.2.3",
        "spotipy==2.23.0",
        "gunicorn==20.1.0",
        "GitPython",
        "python-dotenv==0.21.1",
        "pytest",
        "qdrant-client==1.4.0",
        "werkzeug==2.2.3"
    ],
    package_dir={"": "."},
)