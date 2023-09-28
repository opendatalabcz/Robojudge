import datetime


def parse_date(date_str: str, format: str = "%d. %m. %Y") -> datetime.datetime:
    return datetime.datetime.strptime(date_str, format)
