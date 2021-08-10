import csv
from datetime import datetime

import click
import requests
import sys
import toml
from beautifultable import BeautifulTable
from bs4 import BeautifulSoup
from pages import TimeTrackerPage

from constants import (
    LOGIN_CREDENTIALS, LOAD_HOURS_OPTIONS, WEEKDAYS, BASE_URL,
)
from utils import parse_date

requests.packages.urllib3.disable_warnings()
ADD_TIME_FORM_URL = '{}/TimeTrackerAdd.aspx'


def prepare_session(session):
    """
    Puts in some default headers into a session.
    """
    session.verify = False
    session.headers.update({
        'Host': 'timetracker.bairesdev.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
        'Origin': 'http://timetracker.bairesdev.com',
        'Referer': 'https://timetracker.bairesdev.com/TimeTrackerAdd.aspx',
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
    load_time_url = ADD_TIME_FORM_URL.format(BASE_URL)
    content = session.get(load_time_url).content
    return BeautifulSoup(content, 'html.parser')


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
        values[column_headers.index("Hours")] = rows[-1].find_all('td')[1].string if len(rows[-1].find_all('td')) > 1 else 0.0
        table.append_row(values)
    return table


def check_required(name, available, required):
    for value in required:
        if value not in available:
            raise click.BadParameter(
                "'{}' missing in '{}' config option".format(value, name))


def load_csv_hours(csv_file, config):
    """
    Load csv file hours
    """
    reader = csv.DictReader(csv_file, dialect='excel')
    for row in reader:
        row['pto'] = row.get('pto', False)
        row['vacations'] = row.get('vacations', False)
        if 'date' in row:
            # Allow different date formats to be passed in to csv
            row['date'] = parse_date(row['date']).strftime(r'%d/%m/%Y')
        load_hours(config=config, **row)


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
        options['task-category'] = 'Absence'
        options['task-description'] = 'National Holiday'
        text = text if text is not None else 'PTO'
    if vacations:
        options['task-category'] = 'Absence'
        options['task-description'] = 'Vacations'
        text = text if text is not None else 'Vacations'
    login_page = TimeTrackerPage.start()
    list_page = login_page.login(credentials['username'], credentials['password'])
    ready_page = list_page.ready(project=options['project'], category=options['task-category'])
    ready_page.load(
        date=date,
        task=options['task-description'],
        hours=hours,
        comment=text,
        focal=options['focal']
    )


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
