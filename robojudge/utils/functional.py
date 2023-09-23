import datetime
import asyncio

def parse_date(date_str: str, format: str = '%d. %m. %Y'):
    return datetime.datetime.strptime(date_str, format).isoformat()
# .strftime('%Y-%m-%d')

def periodic(period: int):
    def scheduler(fcn):

        async def wrapper(*args, **kwargs):

            while True:
                asyncio.create_task(fcn(*args, **kwargs))
                await asyncio.sleep(period)

        return wrapper

    return scheduler