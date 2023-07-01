from pydantic import BaseSettings


class Settings(BaseSettings):
    EMBEDDING_CACHE_DIR = 'embedding_models'
    EMBEDDING_MODEL = 'multi-qa-MiniLM-L6-cos-v1'

    class Config:
        env_file = '.env'


settings = Settings()
