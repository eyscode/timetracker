from setuptools import setup, find_packages
import os
import sys

py_version = sys.version_info[:2]

if py_version < (3, 4):
    raise RuntimeError('timetracker-cli requires Python 3.4 or later')

from pathlib import Path

home = str(Path.home())

requirements = [
    'beautifulsoup4==4.7.1',
    'beautifultable==0.7.0',
    'click==7.0',
    'requests==2.22.0',
    'toml==0.10.0',
    'dateparser==0.7.1',
    'tzlocal==1.5.1'
]

setup(
    name='timetracker-cli',
    version='1.1.0',
    description='A command-line utility to interact with BairesDev Time tracker',
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
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Environment :: Console",
        "Operating System :: OS Independent",
    ],
)
