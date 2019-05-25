from setuptools import setup, find_packages
from pathlib import Path
import os

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
    name='timetracker',
    version='1.0.0',
    description='A command-line utility to load hours in BairesDev Time tracker.',
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
    data_files=[(os.path.join(home, '.timetracker'), ['config.toml'])]
)
