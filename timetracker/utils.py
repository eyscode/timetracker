from tzlocal import get_localzone
from dateparser import parse
import click


def parse_date(date):
    return parse(date, date_formats=['%d/%m/%Y'], settings={'TIMEZONE': get_localzone().zone})


def validate_date(ctx, param, date):
    """
    Click helper to turn text into a date.
    """
    parsed_date = parse_date(date)
    if not parsed_date:
        raise click.BadParameter(
            "{} is not a valid date.\n\n".format(date) +
            "Please use 'dd/mm/yyyy' format. " +
            "Values like 'last week', 'yesterday', 'monday', '3 days ago' are also allowed."
        )
    else:
        return parsed_date.strftime(r'%d/%m/%Y')


def begin_of_month():
    return parse_date('today').replace(day=1).strftime(r'%d/%m/%Y')
