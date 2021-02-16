from setuptools import setup, find_packages
import os
import sys

py_version = sys.version_info[:2]

if py_version < (3, 5):
    raise RuntimeError('timetracker-cli requires Python 3.5 or later')

from pathlib import Path

home = str(Path.home())

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()

setup(
    name='timetracker-cli',
    version='1.3.0',
    description='A command-line utility to interact with BairesDev Time tracker',
    long_description=long_description,
    url='https://github.com/eyscode/timetracker/',
    author='Eysenck Gómez',
    author_email='eysenck.gomez@gmail.com',
    packages=find_packages(include=['timetracker']),
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'tt=timetracker.cli:tt',
        ],
    },
    data_files=[(os.path.join(home, '.timetracker'), ['config.toml'])],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
)
