import requests
from bs4 import BeautifulSoup
import click
import toml
from pathlib import Path
import re
import os
import sys
import maya
from tzlocal import get_localzone

HOME = str(Path.home())
CONFIG_PATH = os.path.join(HOME, '.timetracker/config.toml')
BASE_URL = 'http://timetracker.bairesdev.com'

PROJECT_DROPDOWN = 'ctl00_ContentPlaceHolder_idProyectoDropDownList'
ASSIGNMENT_DROPDOWN = 'ctl00_ContentPlaceHolder_idTipoAsignacionDropDownList'
FOCAL_DROPDOWN = 'ctl00_ContentPlaceHolder_idFocalPointClientDropDownList'


def validate_date(ctx, param, date):
    """
    Click helper to turn text into a date.
    """
    try:
        # Maya uses mm/dd/yyyy format, but timetracker uses dd/mm/yyyy format, so we convert it
        localtime = get_localzone().zone
        return maya.when(date, timezone=localtime).datetime(to_timezone=localtime).strftime(r'%d/%m/%Y')
    except:
        raise click.BadParameter(
            f'''{date} is not a valid date.\n\nPlease use 'mm/dd/yyyy' format. Values like 'next week', 'now', 'tomorrow' are also allowed.''')


def prepare_session(session):
    """
    Puts in some default headers into a session.
    """
    session.headers.update({
        'Host': 'timetracker.bairesdev.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
        'Origin': 'http://timetracker.bairesdev.com',
        'Referer': 'http://timetracker.bairesdev.com/'
    })


def login(session, credentials):
    content = session.get(BASE_URL).content
    login_page = BeautifulSoup(content, 'html.parser')
    login_args = {
        'ctl00$ContentPlaceHolder$UserNameTextBox': credentials.get('username'),
        'ctl00$ContentPlaceHolder$PasswordTextBox': credentials.get('password'),
        'ctl00$ContentPlaceHolder$LoginButton': 'Login',
        '__EVENTTARGET': login_page.find('input', {'name': '__EVENTTARGET'}).get('value'),
        '__EVENTARGUMENT': login_page.find('input', {'name': '__EVENTARGUMENT'}).get('value'),
        '__VIEWSTATE': login_page.find('input', {'name': '__VIEWSTATE'}).get('value'),
        '__VIEWSTATEGENERATOR': login_page.find('input', {'name': '__VIEWSTATEGENERATOR'}).get('value'),
        '__EVENTVALIDATION': login_page.find('input', {'name': '__EVENTVALIDATION'}).get('value')
    }
    res = session.post(BASE_URL, data=login_args)
    if not (
            res.history
            and res.history[0].status_code == 302
            and res.status_code == 200
            and res.url == f'{BASE_URL}/ListaTimeTracker.aspx'
    ):
        raise RuntimeError(
            "There was a problem login with your credentials. "
            "Please check them in the config file and try again."
        )


def load_time_form(session):
    """
    Go to the load time form.
    """
    load_time_url = f'{BASE_URL}/CargaTimeTracker.aspx'
    content = session.get(load_time_url).content
    return BeautifulSoup(content, 'html.parser')


def validate_option(form, value, name, _id):
    """
    Validates that you can actually use the configured project.
    """
    options = form.find('select', {'id': _id}).findAll('option')
    options_available = {
        opt.text: opt.get('value')
        for opt in options
        if opt.text
    }
    if not options_available.get(value):
        names = ', '.join(f'"{p}"' for p in options_available.keys())
        raise click.BadParameter(
            f'{name.capitalize()} "{value}" is not available. '
            f'Choose from: {names}'
        )
    return options_available.get(value)


def set_project(session, form, project_option):
    """
    Sets the project into the session so that assignments and focal points become available.
    """
    load_time_url = f'{BASE_URL}/CargaTimeTracker.aspx'
    load_assigments_args = {
        'ctl00$ContentPlaceHolder$ScriptManager': 'ctl00$ContentPlaceHolder$UpdatePanel1|ctl00$ContentPlaceHolder$idProyectoDropDownList',
        '__EVENTTARGET': form.find('input', {'name': '__EVENTTARGET'}).get('value'),
        '__EVENTARGUMENT': form.find('input', {'name': '__EVENTARGUMENT'}).get('value'),
        '__LASTFOCUS': form.find('input', {'name': '__LASTFOCUS'}).get('value'),
        '__VIEWSTATE': form.find('input', {'name': '__VIEWSTATE'}).get('value'),
        '__VIEWSTATEGENERATOR': form.find('input', {'name': '__VIEWSTATEGENERATOR'}).get('value'),
        '__EVENTVALIDATION': form.find('input', {'name': '__EVENTVALIDATION'}).get('value'),
        'ctl00$ContentPlaceHolder$txtFrom': maya.when('today').datetime().strftime("%d/%m/%Y"),
        'ctl00$ContentPlaceHolder$idProyectoDropDownList': project_option,
        'ctl00$ContentPlaceHolder$DescripcionTextBox': '',
        'ctl00$ContentPlaceHolder$TiempoTextBox': '',
        'ctl00$ContentPlaceHolder$idTipoAsignacionDropDownList': '',
        'ctl00$ContentPlaceHolder$idFocalPointClientDropDownList': '',
        '__ASYNCPOST': 'true'
    }
    content = session.post(load_time_url, data=load_assigments_args).content

    _eventtarget = re.search(
        r'hiddenField\|__EVENTTARGET\|([\w*/*\+*=*]*)', str(content)).groups()[0]
    _eventargument = re.search(
        r'hiddenField\|__EVENTARGUMENT\|([\w*/*\+*=*]*)', str(content)).groups()[0]
    _lastfocus = re.search(
        r'hiddenField\|__LASTFOCUS\|([\w*/*\+*]*=*)', str(content)).groups()[0]
    _viewstate = re.search(
        r'hiddenField\|__VIEWSTATE\|([\w*/*\+*]*=*)', str(content)).groups()[0]
    _viewstategenerator = re.search(
        r'hiddenField\|__VIEWSTATEGENERATOR\|([\w*/*\+*=*]*)', str(content)).groups()[0]
    _eventvalidation = re.search(
        r'hiddenField\|__EVENTVALIDATION\|([\w*/*\+*]*=*)', str(content)).groups()[0]
    secrets = {
        '__EVENTTARGET': _eventtarget,
        '__EVENTARGUMENT': _eventargument,
        '__LASTFOCUS': _lastfocus,
        '__VIEWSTATE': _viewstate,
        '__VIEWSTATEGENERATOR': _viewstategenerator,
        '__EVENTVALIDATION': _eventvalidation,

    }

    return secrets, BeautifulSoup(content, 'html.parser')


def actually_load(session, secrets, options):
    load_time_url = f'{BASE_URL}/CargaTimeTracker.aspx'
    load_time_args = {
        **secrets,
        'ctl00$ContentPlaceHolder$txtFrom': options['date'],
        'ctl00$ContentPlaceHolder$idProyectoDropDownList': options['project'],
        'ctl00$ContentPlaceHolder$DescripcionTextBox': options['text'],
        'ctl00$ContentPlaceHolder$TiempoTextBox': options['hours'],
        'ctl00$ContentPlaceHolder$idTipoAsignacionDropDownList': options['assignment'],
        'ctl00$ContentPlaceHolder$idFocalPointClientDropDownList': options.get('focal'),
        'ctl00$ContentPlaceHolder$btnAceptar': 'Accept'
    }

    res = session.post(load_time_url, data=load_time_args)

    if not (
            res.history
            and res.history[0].status_code == 302
            and res.status_code == 200
            and res.url == f'{BASE_URL}/ListaTimeTracker.aspx'
    ):
        raise RuntimeError("There was a problem loading your timetracker :(")


@click.command()
@click.option(
    '--text', '-t',
    help='What did you do?',
)
@click.option(
    '--date', '-d',
    help='When did you do it?',
    default='today',
    callback=validate_date
)
@click.option(
    '--config', '-c',
    default=CONFIG_PATH,
    type=click.Path(exists=True, dir_okay=False),
    help='Path to a config file'
)
@click.option(
    '--pto', '-p',
    default=False,
    is_flag=True,
    help='Is this day paid time off'
)
@click.option(
    '--vacations', '-v',
    default=False,
    is_flag=True,
    help='Is this day paid time off'
)
def load_tt(text, config, date, pto, vacations):
    """
    A command-line utility to load hours in BairesDev Time tracker
    """

    config = toml.load(config)
    credentials = config.get('credentials')
    options = config.get('options')

    if 'username' not in credentials:
        raise click.BadParameter(
            "'username' missing in 'credentials' config option")
    if 'password' not in credentials:
        raise click.BadParameter(
            "'password' missing in 'credentials' config option")
    if 'project' not in options:
        raise click.BadParameter(
            "'project' missing in 'options' config option")
    if 'assignment' not in options:
        raise click.BadParameter(
            "'assignment' missing in 'options' config option")
    if 'focal' not in options:
        raise click.BadParameter("'focal' missing in 'options' config option")
    if 'hours' not in options:
        raise click.BadParameter("'hours' missing in 'options' config option")

    if text is None and not pto and not vacations:
        raise click.BadParameter("You need to specify what you did with --text (-t)")

    if pto:
        options['project'] = 'BairesDev - Absence'
        options['assignment'] = 'National Holiday'
        text = text if text is not None else 'PTO'
    if vacations:
        options['project'] = 'BairesDev - Absence'
        options['assignment'] = 'Vacations'
        text = text if text is not None else 'Vacations'

    session = requests.Session()
    prepare_session(session)

    try:
        login(session, credentials)
    except RuntimeError as e:
        click.echo(f'{e}', err=True, color='red')
        sys.exit(1)

    load_time_page = load_time_form(session)
    project_option = validate_option(
        load_time_page,
        options.get('project'),
        'Project',
        PROJECT_DROPDOWN
    )
    secrets, load_assigments_page = set_project(session, load_time_page, project_option)
    assignment_option = validate_option(
        load_assigments_page,
        options.get('assignment'),
        'Assignment',
        ASSIGNMENT_DROPDOWN
    )

    data = {
        'project': project_option,
        'assignment': assignment_option,
        'text': text,
        'date': date,
        'hours': options.get('hours')
    }

    if not pto and not vacations:
        focal_option = validate_option(
            load_assigments_page,
            options.get('focal'),
            'Focal',
            FOCAL_DROPDOWN
        )
        data['focal'] = focal_option

    try:
        actually_load(session, secrets, data)
        click.echo('success!')
    except RuntimeError as e:
        click.echo(f'{e}', err=True, color='red')
        sys.exit(1)
