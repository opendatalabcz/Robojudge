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
    # Based on the used embedding model's maximum context size with a lower margin (in tokens)
    EMBEDDING_CHUNK_SIZE = 8000
    EMBEDDING_DIMENSIONS = 512

    # Scraping settings
    # Limits the number of rulings than can be queried using semantic search
    MAX_SEARCHABLE_RULING_COUNT: int = 20
    # Allows periodic and automatic scraping
    ENABLE_AUTOMATIC_SCRAPING: bool = True
    # How many rulings a single scraping job will attempt to scrape
    SCRAPER_SINGLE_RUN_RULING_COUNT = 10
    # The frequency of running periodic scraping - once per day is the most sensible (https://crontab.guru/#*/2_*_*_*_*)
    SCRAPER_CRONTAB = "0 1 * * *"
    # No rulings could have appeared sooner than this date
    FIRST_JUSTICE_DB_DATE = "2020-11-28"
    # Limit the number of dates scraped for demo purposes
    MAX_DATES_COUNT = 720
    # Number of seconds to wait between adding another date to fetch rulings for (for DB initialization)
    BASE_FETCH_JOB_INTERVAL = 0.9
    # Number of seconds added to the interval if a failure happens
    FAILED_FETCH_JOB_INTERVAL_INCREASE = 1
    # Number of seconds subtracted from the interval if a success happens (BASE is always the minimum)
    SUCCESSFUL_FETCH_JOB_INTERVAL_INCREASE = 0.1
    # In case of a failed scraping job (not because of an individual ruling failure, but the whole job failing), try again this number of times
    MAX_RETRIES: int = 2

    # LLM settings
    OPENAI_API_KEY = "dummykey"
    OPENAI_API_BASE = "https://api.openai.com/v1"
    OPENAI_API_VERSION = "2023-08-01-preview"
    INAPP_GPT_MODEL_NAME = "gpt-3.5-turbo-1106"
    EMBEDDER_MODEL_NAME = "text-embedding-3-small"

    # Research settings
    AUTO_EVALUATOR_NAME = "gpt-4-1106-preview"
    REPLICATE_API_TOKEN: str = ""
    COHERE_API_TOKEN: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
