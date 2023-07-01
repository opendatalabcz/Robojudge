from case_page_scraper import CasePageScraper

# Take last found id on the main page
# Scrape until your reach your newest case_id in DB


async def scrape_cases():
    latest_case_id = await CasePageScraper.get_newest_case_id()

    # last_case_id_in_db = 

