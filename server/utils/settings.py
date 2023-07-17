from pydantic import BaseSettings


class Settings(BaseSettings):
    SERVER_PORT = 4000
    SERVER_VERSION = '0.1.0'
    ENVIRONMENT = 'dev'

    CLIENT_HOST = 'http://localhost'
    CLIENT_PORT = 3000

    EMBEDDING_DB_HOST = 'localhost'
    EMBEDDING_DB_PORT = 8000
    EMBEDDING_CACHE_DIR = 'embedding_models'
    EMBEDDING_MODEL = 'multi-qa-MiniLM-L6-cos-v1'

    MONGODB_URL = "mongodb://root:example@localhost:27017"

    SCRAPER_TIMEOUT = 10_000

    LOG_LEVEL = 'DEBUG'

    class Config:
        env_file = '.env'


settings = Settings()
