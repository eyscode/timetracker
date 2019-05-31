import click

from .timetracker import load_hours, show_hours
from .constants import CONFIG_PATH
from .utils import validate_date, begin_of_month


@click.group()
def tt():
    """
    A command-line utility to interact with BairesDev Time tracker
    """


@tt.command()
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
@click.option(
    '--hours', '-h',
    help='How long did it take?',
)
def load(text, config, date, pto, vacations, hours):
    """
    Load hours
    """
    load_hours(text, config, date, pto, vacations, hours)


@tt.command()
@click.option(
    '--config', '-c',
    default=CONFIG_PATH,
    type=click.Path(exists=True, dir_okay=False),
    help='Path to a config file'
)
@click.option(
    '--start', '-s',
    help='Starting date',
    default=begin_of_month,
    callback=validate_date
)
@click.option(
    '--end', '-e',
    help='End date',
    default='today',
    callback=validate_date
)
@click.option(
    '--full', '-f',
    is_flag=True,
    help='Show full table',
    default=False
)
@click.option(
    '--weekday', '-w',
    is_flag=True,
    help='Show week day',
    default=False
)
def show(config, start, end, full, weekday):
    """
    Show loaded hours
    """
    show_hours(config, start, end, full, weekday)
