import requests
from bs4 import BeautifulSoup
import click
import toml
from pathlib import Path
import datetime
import re
import os
import sys

home = str(Path.home())
default_config_path = os.path.join(home, '.timetracker/config.toml')


def today():
    return datetime.datetime.today().strftime("%d/%m/%Y")


def validate_date(ctx, param, date):
    s = re.match(
        '^(?P<day>today|yesterday)(-(?P<before>[0-9]+))*$', date)
    if re.match('^[0-3][0-9]/[0-1][0-9]/[1-2][0-9][0-9][0-9]$', date):
        return date
    elif s:
        params = s.groupdict()
        days_before = 0
        if params.get('before'):
            days_before += int(params.get('before'))
        if params.get('day') == 'yesterday':
            days_before += 1
        return (datetime.datetime.today() - datetime.timedelta(days=days_before)).strftime("%d/%m/%Y")
    else:
        raise click.BadParameter(
            "date must be in format dd/mm/yyyy. 'today', 'yesterday', 'today-1', 'today-[number]' are also supported")


help_text = 'Text description of the hours you are tracking'
help_config = 'Path to the config file'
help_date = "Date in format dd/mm/yyyy. 'today', 'yesterday', 'today-1', 'today-[number]' are also supported"


@click.command()
@click.option('--text', '-t', help=help_text, required=True)
@click.option('--config', '-c', default=default_config_path, type=click.Path(exists=True), help=help_config)
@click.option('--date', '-d', default=today, help=help_date, callback=validate_date)
def load_tt(text, config, date):
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

    initial_headers = {
        'Host': 'timetracker.bairesdev.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
        'Origin': 'http://timetracker.bairesdev.com',
        'Referer': 'http://timetracker.bairesdev.com/'
    }

    session = requests.Session()
    session.headers.update(initial_headers)

    base_url = 'http://timetracker.bairesdev.com/'

    login_page = BeautifulSoup(session.get(base_url).content, 'html.parser')
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

    res = session.post(base_url, data=login_args)

    if not (res.history and res.history[
            0].status_code == 302 and res.status_code == 200 and res.url == 'http://timetracker.bairesdev.com/ListaTimeTracker.aspx'):
        print("There was a problem login with your credentials. Please check them in the config file and try again.", file=sys.stderr)
        return

    load_time_url = 'http://timetracker.bairesdev.com/CargaTimeTracker.aspx'

    load_time_page = BeautifulSoup(session.get(
        load_time_url).content, 'html.parser')

    projects_available = {
        opt.text: opt.get('value') for opt in load_time_page.find(
            'select', {'id': 'ctl00_ContentPlaceHolder_idProyectoDropDownList'}).findAll('option') if opt.text
    }

    if not projects_available.get(options.get('project')):
        raise click.BadParameter(
            "Project '{}' is not available. Specify a valid project name. Available projects: {}".format(
                options.get('project'), ", ".join(("'{}'").format(a) for a in projects_available.keys())))

    load_assigments_args = {
        'ctl00$ContentPlaceHolder$ScriptManager': 'ctl00$ContentPlaceHolder$UpdatePanel1|ctl00$ContentPlaceHolder$idProyectoDropDownList',
        '__EVENTTARGET': load_time_page.find('input', {'name': '__EVENTTARGET'}).get('value'),
        '__EVENTARGUMENT': load_time_page.find('input', {'name': '__EVENTARGUMENT'}).get('value'),
        '__LASTFOCUS': load_time_page.find('input', {'name': '__LASTFOCUS'}).get('value'),
        '__VIEWSTATE': load_time_page.find('input', {'name': '__VIEWSTATE'}).get('value'),
        '__VIEWSTATEGENERATOR': load_time_page.find('input', {'name': '__VIEWSTATEGENERATOR'}).get('value'),
        '__EVENTVALIDATION': load_time_page.find('input', {'name': '__EVENTVALIDATION'}).get('value'),
        'ctl00$ContentPlaceHolder$txtFrom': datetime.datetime.today().strftime("%d/%m/%Y"),
        'ctl00$ContentPlaceHolder$idProyectoDropDownList': projects_available.get(options.get('project')),
        'ctl00$ContentPlaceHolder$DescripcionTextBox': '',
        'ctl00$ContentPlaceHolder$TiempoTextBox': '',
        'ctl00$ContentPlaceHolder$idTipoAsignacionDropDownList': '',
        'ctl00$ContentPlaceHolder$idFocalPointClientDropDownList': '',
        '__ASYNCPOST': 'true'
    }

    raw_data = session.post(load_time_url, data=load_assigments_args).content

    load_assigments_page = BeautifulSoup(raw_data, 'html.parser')

    assigments_available = {
        opt.text: opt.get('value') for opt in load_assigments_page.find(
            'select', {'id': 'ctl00_ContentPlaceHolder_idTipoAsignacionDropDownList'}).findAll('option') if opt.text
    }

    focals_available = {
        opt.text: opt.get('value') for opt in load_assigments_page.find(
            'select', {'id': 'ctl00_ContentPlaceHolder_idFocalPointClientDropDownList'}).findAll('option') if opt.text
    }

    if not assigments_available.get(options.get('assignment')):
        raise click.BadParameter(
            "Assignment '{}' is not available. Specify a valid assignment name. Available assigments: {}".format(
                options.get('assignment'), ", ".join(("'{}'").format(a) for a in assigments_available.keys())))
    if not focals_available.get(options.get('focal')):
        raise click.BadParameter(
            "Focal point '{}' is not available. Specify a valid focal point name. Available focal points: {}".format(
                options.get('focal'), ", ".join(("'{}'").format(a) for a in focals_available.keys())))

    _eventtarget = re.search(
        r'hiddenField\|__EVENTTARGET\|([\w*/*\+*=*]*)', str(raw_data)).groups()[0]
    _eventargument = re.search(
        r'hiddenField\|__EVENTARGUMENT\|([\w*/*\+*=*]*)', str(raw_data)).groups()[0]
    _lastfocus = re.search(
        r'hiddenField\|__LASTFOCUS\|([\w*/*\+*]*=*)', str(raw_data)).groups()[0]
    _viewstate = re.search(
        r'hiddenField\|__VIEWSTATE\|([\w*/*\+*]*=*)', str(raw_data)).groups()[0]
    _viewstategenerator = re.search(
        r'hiddenField\|__VIEWSTATEGENERATOR\|([\w*/*\+*=*]*)', str(raw_data)).groups()[0]
    _eventvalidation = re.search(
        r'hiddenField\|__EVENTVALIDATION\|([\w*/*\+*]*=*)', str(raw_data)).groups()[0]

    load_time_args = {
        '__EVENTTARGET': _eventtarget,
        '__EVENTARGUMENT': _eventargument,
        '__LASTFOCUS': _lastfocus,
        '__VIEWSTATE': _viewstate,
        '__VIEWSTATEGENERATOR': _viewstategenerator,
        '__EVENTVALIDATION': _eventvalidation,
        'ctl00$ContentPlaceHolder$txtFrom': date,
        'ctl00$ContentPlaceHolder$idProyectoDropDownList': projects_available.get(options.get('project')),
        'ctl00$ContentPlaceHolder$DescripcionTextBox': text,
        'ctl00$ContentPlaceHolder$TiempoTextBox': options.get('hours'),
        'ctl00$ContentPlaceHolder$idTipoAsignacionDropDownList': assigments_available.get(options.get('assignment')),
        'ctl00$ContentPlaceHolder$idFocalPointClientDropDownList': focals_available.get(options.get('focal')),
        'ctl00$ContentPlaceHolder$btnAceptar': 'Accept'
    }

    res = session.post(load_time_url, data=load_time_args)

    if res.history and res.history[0].status_code == 302 and res.status_code == 200 and res.url == 'http://timetracker.bairesdev.com/ListaTimeTracker.aspx':
        print("Done!")
    else:
        print("There was a problem loading your hours :(", file=sys.stderr)
