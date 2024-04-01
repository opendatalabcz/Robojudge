from pydantic import BaseSettings

SUMMARY_UNAVAILABLE_MESSAGE = "Nebylo možné vygenerovat shrnutí."


class Settings(BaseSettings):
    # Basic server settings
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 4000
    SERVER_VERSION = "0.1.0"
    ENVIRONMENT = "dev"
    LOG_LEVEL = "INFO"

    # Connection settings
    CLIENT_HOST = "http://localhost"
    CLIENT_PORT = 3000
    EMBEDDING_DB_HOST = "chroma"
    EMBEDDING_DB_PORT = 8000
    DOCUMENT_DB_HOST = "mongo"
    DOCUMENT_DB_PORT: int = 27017
    REDIS_URL: str = "localhost"
    RABBIT_HOST: str = "localhost"
    RABBIT_PORT: int = 5672

    # Used for splitting ruling and query texts
    # Based on the used embedding model's maximum context size (in tokens)
    EMBEDDING_CHUNK_SIZE = 256

    # Scraping settings
    # Limits the number of cases than can be queried using semantic search
    MAX_SEARCHABLE_RULING_COUNT: int = 20
    # Allows periodic and automatic scraping
    ENABLE_AUTOMATIC_SCRAPING: bool = True
    # In case no rulings are scraped based on a set of IDs, the scraper will increasingly try bigger gaps before it finds rulings.
    # This is the maximum by much it will be allowed to jump.
    SCRAPER_MAX_EMPTY_JUMP = 5000
    # How many rulings a single scraping job will attempt to scrape
    SCRAPER_SINGLE_RUN_CASE_COUNT = 20
    # The scraper will wait for page loading at most this much (milliseconds)
    SCRAPER_TIMEOUT = 10_000
    # How many scrapers should be periodically run (in parallel)
    PARALLEL_SCRAPER_INSTANCES = 2
    # The frequency of running periodic scraping (https://crontab.guru/#*/2_*_*_*_*)
    SCRAPER_CRONTAB = "*/2 * * * *"
    # Will scrape rulings from the newest to the oldest
    SCRAPE_CASES_FROM_LAST: bool = False
    # Based on manual testing, this is one of the first available cases
    OLDEST_KNOWN_CASE_ID = 450
    # In case of a failed scraping job (not because of an individual ruling failure, but the whole job failing), try again this number of times
    MAX_RETRIES: int = 2
    # The scraper will wait at least this number of milliseconds before retrying a failed job
    MIN_BACKOFF: str = 15_000

    # LLM settings
    OPENAI_API_KEY = "dummykey"
    OPENAI_API_BASE = "https://api.openai.com/v1"
    OPENAI_API_VERSION = "2023-08-01-preview"
    INAPP_GPT_MODEL_NAME = "gpt-3.5-turbo-1106"

    # Research settings
    AUTO_EVALUATOR_NAME = "gpt-4-1106-preview"
    REPLICATE_API_TOKEN: str = ""
    COHERE_API_TOKEN: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
