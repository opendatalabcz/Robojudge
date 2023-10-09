import datetime
import uuid


def parse_date(date_str: str, format: str = "%d. %m. %Y") -> datetime.datetime:
    return datetime.datetime.strptime(date_str, format)


def generate_uuid():
    return str(uuid.uuid4())
