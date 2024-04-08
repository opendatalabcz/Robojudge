import datetime

import httpx

from robojudge.utils.functional import parse_date
from robojudge.utils.internal_types import Ruling, RulingMetadata
from robojudge.utils.logger import logger


class RulingScraper:
    JUSTICE_API_BASE_URL = "https://rozhodnuti.justice.cz/api/opendata"

    @classmethod
    async def get_ruling_infos_for_date(
        cls, date: datetime.datetime | str
    ) -> list[dict]:
        if not isinstance(date, str):
            try:
                date = datetime.date.isoformat(date)
            except Exception:
                logger.error(
                    f'Provided date {date} cannot be converted to "YYYY-MM-DD".'
                )

        # The endpoint is divided into subpaths like .../<year>/<month>/<day>
        date = date.replace("-", "/")

        date_url = cls.JUSTICE_API_BASE_URL + f"/{date}"

        async with httpx.AsyncClient(timeout=600) as client:
            try:
                # The endpoint is paginated, the first (zeroth) page is implicit.
                ruling_infos, response = await cls.get_rulings_list_page(date_url, client)

                if (total_pages := response.get("totalPages")) != 1:
                    for page_num in range(1, total_pages):
                        rulings_url = date_url + f"?page={page_num}"
                        page_ruling_infos, _ = await cls.get_rulings_list_page(
                            rulings_url, client
                        )
                        ruling_infos.extend(page_ruling_infos)

                return ruling_infos
            except Exception as e:
                logger.error(f'Error while getting rulings from "{date_url}":', error=e)
                return []

    @classmethod
    async def get_rulings_list_page(
        cls, rulings_url: str, client: httpx.AsyncClient
    ) -> tuple[list[dict], dict]:
        try:
            res = await client.get(rulings_url)
            res.raise_for_status()

            rulings_raw = res.json()

            ruling_infos = []
            for ruling_info in rulings_raw.get("items", []):
                if ruling_info.get("odkaz", None):
                    ruling_infos.append(ruling_info)

            return ruling_infos, rulings_raw
        except Exception as e:
            logger.error(f'Error while getting rulings from "{rulings_url}":', error=e)
            raise e

    @classmethod
    async def get_ruling_by_url(
        cls, ruling_info: dict, client: httpx.AsyncClient
    ) -> tuple[Ruling, dict]:
        ruling_url = ruling_info.get("odkaz")
        try:
            sentence_date = parse_date(ruling_info.get("datumVydani", ""), "%Y-%m-%d")
            publication_date = parse_date(
                ruling_info.get("datumZverejneni", ""), "%Y-%m-%d"
            )

            res = await client.get(ruling_url)
            res.raise_for_status()

            ruling_raw = res.json()
            metadata_raw = ruling_raw.get("metadata")

            # TODO: check related rulings format

            metadata = RulingMetadata(
                type=metadata_raw.get("type", ""),
                jednaci_cislo=ruling_info.get("jednaciCislo", ""),
                url=ruling_url,
                ecli_id=ruling_info.get("ecli", ""),
                sentence_date=sentence_date,
                publication_date=publication_date,
                judge_name=ruling_info.get("autor", ""),
                court=ruling_info.get("soud"),
                subject_matter=ruling_info.get("predmetRizeni", ""),
                keywords=ruling_info.get("klicovaSlova", []),
                regulations_mentioned=ruling_info.get("zminenaUstanoveni", []),
                # related_rulings=metadata_raw.get("affectedDocs", []),
            )

            ruling = Ruling(
                ruling_id=ruling_raw.get("uuid", ""),
                verdict=ruling_raw.get("verdictText", ""),
                reasoning=ruling_raw.get("justificationText", ""),
                metadata=metadata,
            )

            return ruling, None

        except Exception as e:
            logger.error(
                f'Error while getting ruling with url "{ruling_url}":', error=e
            )
            return None, ruling_info

    @classmethod
    def get_ruling_dates_since_justice_db_start(
        cls, start_date: str = None
    ) -> list[str]:
        dates = []
        start_date = datetime.datetime.strptime(
            start_date, "%Y-%m-%d"
        ) + datetime.timedelta(days=1)
        end_date = datetime.datetime.today()

        delta = end_date - start_date

        for i in range(delta.days):
            date = start_date + datetime.timedelta(days=i)
            dates.append(date.strftime("%Y-%m-%d"))

        return dates
        # async with httpx.AsyncClient() as client:
        #     res = await client.get(cls.JUSTICE_API_BASE_URL, timeout=600)
        #     res.raise_for_status()

        #     dates_raw = res.json()
        #     return [obj.get("datum", "") for obj in dates_raw if obj.get("datum", "")]
