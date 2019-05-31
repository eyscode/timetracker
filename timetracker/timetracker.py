from copy import copy
from datetime import datetime

import requests
from beautifultable import BeautifulTable
from bs4 import BeautifulSoup
import click
import toml
import re
import sys

from .utils import parse_date
from .constants import (
    PROJECT_DROPDOWN, FOCAL_DROPDOWN, ASSIGNMENT_DROPDOWN, LOGIN_CREDENTIALS, LOAD_HOURS_OPTIONS, WEEKDAYS, BASE_URL
)


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
        '__VIEWSTATE': login_page.find('input', {'name': '__VIEWSTATE'}).get('value'),
        '__VIEWSTATEGENERATOR': login_page.find('input', {'name': '__VIEWSTATEGENERATOR'}).get('value'),
        '__EVENTVALIDATION': login_page.find('input', {'name': '__EVENTVALIDATION'}).get('value')
    }
    res = session.post(BASE_URL, data=login_args)
    if not (
            res.history
            and res.history[0].status_code == 302
            and res.status_code == 200
            and res.url == '{}/ListaTimeTracker.aspx'.format(BASE_URL)
    ):
        raise RuntimeError(
            "There was a problem login with your credentials. "
            "Please check them in the config file and try again."
        )
    return BeautifulSoup(res.content, 'html.parser')


def load_time_form(session):
    """
    Go to the load time form.
    """
    load_time_url = '{}/CargaTimeTracker.aspx'.format(BASE_URL)
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
        names = ', '.join('"{}"'.format(p) for p in options_available.keys())
        raise click.BadParameter(
            '{} "{}" is not available. Choose from: {}'.format(name.capitalize(), value, names)
        )
    return options_available.get(value)


def fetch_hours(session, form, start, end):
    """
    Fetches list of loaded hours
    """
    list_time_url = '{}/ListaTimeTracker.aspx'.format(BASE_URL)
    args = {
        '__EVENTTARGET': 'ctl00$ContentPlaceHolder$AplicarFiltroLinkButton',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': form.find('input', {'name': '__VIEWSTATE'}).get('value'),
        '__VIEWSTATEGENERATOR': form.find('input', {'name': '__VIEWSTATEGENERATOR'}).get('value'),
        '__VIEWSTATEENCRYPTED': '',
        '__EVENTVALIDATION': form.find('input', {'name': '__EVENTVALIDATION'}).get('value'),
        'ctl00$ContentPlaceHolder$txtFrom': start,
        'ctl00$ContentPlaceHolder$txtTo': end
    }
    content = session.post(list_time_url, data=args).content
    return BeautifulSoup(content, 'html.parser')


def set_project(session, form, project_option):
    """
    Sets the project into the session so that assignments and focal points become available.
    """
    load_time_url = '{}/CargaTimeTracker.aspx'.format(BASE_URL)
    load_assigments_args = {
        'ctl00$ContentPlaceHolder$ScriptManager': 'ctl00$ContentPlaceHolder$UpdatePanel1|ctl00$ContentPlaceHolder$idProyectoDropDownList',
        '__VIEWSTATE': form.find('input', {'name': '__VIEWSTATE'}).get('value'),
        '__VIEWSTATEGENERATOR': form.find('input', {'name': '__VIEWSTATEGENERATOR'}).get('value'),
        '__EVENTVALIDATION': form.find('input', {'name': '__EVENTVALIDATION'}).get('value'),
        'ctl00$ContentPlaceHolder$txtFrom': parse_date('today').strftime(r'%d/%m/%Y'),
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


def hours_as_table(content, current_month, full, show_weekday):
    """
    Validates that you can actually use the configured project.
    """
    table = BeautifulTable()
    if full:
        column_headers = ["Date", "Hours", "Project", "Assigment Type", "Description"]
    else:
        column_headers = ["Date", "Description"]

    if show_weekday:
        column_headers = ["Weekday"] + column_headers

    table.column_headers = column_headers

    rows = content.find(class_='tbl-respuestas').find_all('tr')

    for row in rows[:-1]:
        cols = row.find_all('td')
        if cols:
            date = cols[0].string if not current_month else cols[0].string[:2]
            if full:
                values = [date, cols[1].string, cols[2].string, cols[3].string, cols[4].string]
            else:
                values = [date, cols[4].string]
            if show_weekday:
                weekday = datetime.strptime(cols[0].string, r'%d/%m/%Y').weekday()
                values = [WEEKDAYS[weekday]] + values
            table.append_row(values)

    if full:
        values = ["" for i in range(len(column_headers))]
        values[column_headers.index("Hours")] = rows[-1].find_all('td')[1].string
        table.append_row(values)
    return table


def actually_load(session, secrets, options):
    load_time_url = '{}/CargaTimeTracker.aspx'.format(BASE_URL)
    load_time_args = copy(secrets)
    load_time_args.update({
        'ctl00$ContentPlaceHolder$txtFrom': options['date'],
        'ctl00$ContentPlaceHolder$idProyectoDropDownList': options['project'],
        'ctl00$ContentPlaceHolder$DescripcionTextBox': options['text'],
        'ctl00$ContentPlaceHolder$TiempoTextBox': options['hours'],
        'ctl00$ContentPlaceHolder$idTipoAsignacionDropDownList': options['assignment'],
        'ctl00$ContentPlaceHolder$idFocalPointClientDropDownList': options.get('focal'),
        'ctl00$ContentPlaceHolder$btnAceptar': 'Accept'
    })

    res = session.post(load_time_url, data=load_time_args)

    if not (
            res.history
            and res.history[0].status_code == 302
            and res.status_code == 200
            and res.url == '{}/ListaTimeTracker.aspx'.format(BASE_URL)
    ):
        raise RuntimeError("There was a problem loading your timetracker :(")


def check_required(name, available, required):
    for value in required:
        if value not in available:
            raise click.BadParameter(
                "'{}' missing in '{}' config option".format(value, name))


def load_hours(text, config, date, pto, vacations, hours):
    config = toml.load(config)
    credentials = config.get('credentials')
    options = config.get('options')

    check_required('credentials', credentials, LOGIN_CREDENTIALS)
    check_required('options', options, LOAD_HOURS_OPTIONS)

    if text is None and not pto and not vacations:
        raise click.BadParameter("You need to specify what you did with --text (-t)")

    if hours is None:
        hours = options.get('hours')

    if hours is None:
        raise click.BadParameter("You need to specify hours amount with --hours (-h) or using hours options in config.toml")


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
        click.echo('{}'.format(e), err=True, color='red')
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
        'hours': hours
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
        click.echo('{}'.format(e), err=True, color='red')
        sys.exit(1)


def show_hours(config, start, end, full, weekday):
    config = toml.load(config)
    credentials = config.get('credentials')
    check_required('credentials', credentials, LOGIN_CREDENTIALS)

    session = requests.Session()
    prepare_session(session)

    try:
        hour_list = login(session, credentials)
    except RuntimeError as e:
        click.echo('{}'.format(e), err=True, color='red')
        sys.exit(1)

    hour_list = fetch_hours(session, hour_list, start, end)
    click.echo("Start: {}, End: {}".format(start, end))

    click.echo(hours_as_table(hour_list, current_month=not start and not end, full=full, show_weekday=weekday))
