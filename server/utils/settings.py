from pydantic import BaseSettings


class Settings(BaseSettings):
    APP_PORT=4000
    ENVIRONMENT='dev'

    EMBEDDING_DB_HOST='localhost'
    EMBEDDING_DB_PORT=8000
    EMBEDDING_CACHE_DIR = 'embedding_models'
    EMBEDDING_MODEL = 'multi-qa-MiniLM-L6-cos-v1'

    MONGODB_URL = "mongodb://root:example@localhost:27017"

    SCRAPER_TIMEOUT = 10_000

    LOG_LEVEL = 'DEBUG'

    class Config:
        env_file = '.env'


settings = Settings()
