import datetime
import uuid

from robojudge.utils.settings import settings


def construct_server_url(suffix: str = ""):
    return f"http://{settings.SERVER_HOST}:{settings.SERVER_PORT}" + suffix


def parse_date(date_str: str, format: str = "%d. %m. %Y") -> datetime.datetime:
    return datetime.datetime.strptime(date_str, format)


def extract_ruling_id(url: str):
    return url.split("/")[-1]


def generate_uuid():
    return str(uuid.uuid4())
