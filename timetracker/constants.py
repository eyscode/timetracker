from pathlib import Path
import os

HOME = str(Path.home())
CONFIG_PATH = os.path.join(HOME, '.timetracker/config.toml')
BASE_URL = 'https://timetracker.bairesdev.com'

LOGIN_CREDENTIALS = ['username', 'password']
LOAD_HOURS_OPTIONS = ['project', 'task-category', 'task-description', 'focal']

WEEKDAYS = ['M', 'T', 'W', 'TH', 'F', 'S', 'SU']
