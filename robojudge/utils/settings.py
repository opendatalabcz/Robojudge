from pydantic import BaseSettings
from langchain.chat_models import AzureChatOpenAI


class Settings(BaseSettings):
    SERVER_PORT = 4000
    SERVER_VERSION = "0.1.0"
    ENVIRONMENT = "dev"

    CLIENT_HOST = "http://localhost"
    CLIENT_PORT = 3000

    EMBEDDING_DB_PATH = "chroma"
    EMBEDDING_DB_HOST = "localhost"
    EMBEDDING_DB_PORT = 8000
    EMBEDDING_CACHE_DIR = "embedding_models"
    # EMBEDDING_MODEL = 'multi-qa-MiniLM-L6-cos-v1'

    MONGODB_URL = "mongodb://mongo:27017"  # Depends on the name of the container in docker-compose

    SCRAPER_TIMEOUT = 10_000

    LOG_LEVEL = "DEBUG"

    OPENAI_API_KEY = ""
    OPENAI_API_BASE = ""
    OPENAI_API_TYPE = "azure"
    OPENAI_API_VERSION = "2023-05-15"
    GPT_MODEL_NAME = "gpt-35-turbo-16k"

    BARD__Secure_1PSID = ""
    BARD__Secure_1PSIDTS = ""

    TOKENIZER_INPUT_LENGTH = 600
    TOKENIZER_MODEL = "czech-morfflex2.0-pdtc1.0-220710"
    TOKENIZER_URL = "http://lindat.mff.cuni.cz/services/morphodita/api/tag"

    OLDEST_KNOWN_CASE_ID = (
        450  # Based on manual testing, this is one of the first available cases
    )

    DEFAULT_SUMMARIZE_LLM = "chatgpt"
    SUMMARIZE_MAX_PARALLEL_REQUESTS = 1

    AGENT_MAX_EXECUTION_TIME = 120

    class Config:
        env_file = ".env"


settings = Settings()

LLM_BASIC_SETTINGS = {
    "openai_api_key": settings.OPENAI_API_KEY,
    "openai_api_base": settings.OPENAI_API_BASE,
    "openai_api_version": settings.OPENAI_API_VERSION,
    "openai_api_type": settings.OPENAI_API_TYPE,
}


standard_llm = AzureChatOpenAI(
    **LLM_BASIC_SETTINGS, deployment_name=settings.DEFAULT_SUMMARIZE_LLM, temperature=0
)
