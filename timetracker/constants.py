from pathlib import Path
import os

HOME = str(Path.home())
CONFIG_PATH = os.path.join(HOME, '.timetracker/config.toml')
BASE_URL = 'https://timetracker.bairesdev.com'

PROJECT_DROPDOWN = 'ctl00_ContentPlaceHolder_idProyectoDropDownList'
CATEGORY_DROPDOWN = 'ctl00_ContentPlaceHolder_idCategoriaTareaXCargoLaboralDropDownList'
DESCRIPTION_DROPDOWN = 'ctl00_ContentPlaceHolder_idTareaXCargoLaboralDownList'
FOCAL_DROPDOWN = 'ctl00_ContentPlaceHolder_idFocalPointClientDropDownList'

LOGIN_CREDENTIALS = ['username', 'password']
LOAD_HOURS_OPTIONS = ['project', 'assignment', 'focal']

WEEKDAYS = ['M', 'T', 'W', 'TH', 'F', 'S', 'SU']
