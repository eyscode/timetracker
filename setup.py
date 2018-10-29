from setuptools import setup, find_packages
from pathlib import Path
import os

home = str(Path.home())


requirements = [
    'beautifulsoup4==4.6.0',
    'click==6.7',
    'requests==2.18.4',
    'toml==0.9.4',
    'beautifulsoup4==4.6.0',
    'maya==0.5.0'
]

setup(
    name='timetracker',
    version='0.1',
    description='A command-line utility to load hours in BairesDev Time tracker.',
    url='https://github.com/eyscode/timetracker/',
    author='Eysenck Gómez',
    author_email='eyscode@gmail.com',
    py_modules=['load_tt'],
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        load-tt=load_tt:load_tt
    ''',
    data_files=[(os.path.join(home, '.timetracker'), ['config.toml'])]
)
