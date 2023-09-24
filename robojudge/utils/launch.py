import uvicorn
from rocketry import Rocketry
from rocketry.conds import every

from robojudge.utils.settings import settings
from robojudge.tasks.case_scraping import run_scraping_instance

app = Rocketry(config={"task_execution": "async"})


@app.task(every(f"{settings.SCRAPER_TASK_INTERVAL_IN_SECONDS} seconds"))
async def case_scraping():
    await run_scraping_instance()


# https://itnext.io/scheduler-with-an-api-rocketry-fastapi-a0f742278d5b
class Server(uvicorn.Server):
    """Customized uvicorn.Server

    Uvicorn server overrides signals and we need to include
    Rocketry to the signals."""

    def handle_exit(self, sig: int, frame) -> None:
        app.session.shut_down()
        return super().handle_exit(sig, frame)

