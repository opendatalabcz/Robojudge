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

    MONGODB_URL = "mongodb://localhost:27017"

    SCRAPER_TIMEOUT = 10_000

    LOG_LEVEL = 'DEBUG'

    OPENAI_API_KEY = ''
    OPENAI_API_BASE = ''
    GPT_MODEL_NAME='chatgpt'

    BARD__Secure_1PSID = ''
    BARD__Secure_1PSIDTS = ''

    TOKENIZER_INPUT_LENGTH = 600
    TOKENIZER_MODEL = 'czech-morfflex2.0-pdtc1.0-220710'
    TOKENIZER_URL = 'http://lindat.mff.cuni.cz/services/morphodita/api/tag'

    OLDEST_KNOWN_CASE_ID = 450  # Based on manual testing, this is one of the first available cases

    DEFAULT_SUMMARIZE_LLM = 'chatgpt'
    SUMMARIZE_MAX_PARALLEL_REQUESTS=4

    class Config:
        env_file = '.env'


settings = Settings()
