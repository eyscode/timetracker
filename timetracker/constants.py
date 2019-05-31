from pathlib import Path
import os

HOME = str(Path.home())
CONFIG_PATH = os.path.join(HOME, '.timetracker/config.toml')
BASE_URL = 'https://timetracker.bairesdev.com'

PROJECT_DROPDOWN = 'ctl00_ContentPlaceHolder_idProyectoDropDownList'
ASSIGNMENT_DROPDOWN = 'ctl00_ContentPlaceHolder_idTipoAsignacionDropDownList'
FOCAL_DROPDOWN = 'ctl00_ContentPlaceHolder_idFocalPointClientDropDownList'

LOGIN_CREDENTIALS = ['username', 'password']
LOAD_HOURS_OPTIONS = ['project', 'assignment', 'focal']

WEEKDAYS = ['M', 'T', 'W', 'TH', 'F', 'S', 'SU']
