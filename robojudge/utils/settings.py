from pydantic import BaseSettings
from langchain.chat_models import AzureChatOpenAI


class Settings(BaseSettings):
    SERVER_PORT = 4000
    SERVER_VERSION = "0.1.0"
    ENVIRONMENT = "dev"
    LOG_LEVEL = "DEBUG"

    CLIENT_HOST = "http://localhost"
    CLIENT_PORT = 3000

    EMBEDDING_DB_HOST = "chroma"
    EMBEDDING_DB_PORT = 8000
    EMBEDDING_CHUNK_SIZE = 500

    DOCUMENT_DB_HOST = 'mongo'
    DOCUMENT_DB_PORT: int = 27017

    SCRAPER_MAX_RUN_CASE_COUNT = 30
    SCRAPER_TIMEOUT = 10_000
    SCRAPER_TASK_INTERVAL_IN_SECONDS = 3600
    OLDEST_KNOWN_CASE_ID = (
        450  # Based on manual testing, this is one of the first available cases
    )

    OPENAI_API_KEY = ""
    OPENAI_API_BASE = ""
    OPENAI_API_TYPE = "azure"
    OPENAI_API_VERSION = "2023-05-15"

    # Research summarizing
    GPT_MODEL_NAME = "gpt-35-turbo-16k"
    BARD__Secure_1PSID = ""
    BARD__Secure_1PSIDTS = ""
    SUMMARIZE_MAX_PARALLEL_REQUESTS = 1
    DEFAULT_SUMMARIZE_LLM = "chatgpt"

    TOKENIZER_INPUT_LENGTH = 600
    TOKENIZER_MODEL = "czech-morfflex2.0-pdtc1.0-220710"
    TOKENIZER_URL = "http://lindat.mff.cuni.cz/services/morphodita/api/tag"

    # App summarizing
    SUMMARIZE_LLM_MODEL = 'chatgpt'
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
    **LLM_BASIC_SETTINGS, deployment_name=settings.SUMMARIZE_LLM_MODEL, temperature=0
)
