from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Script Management API"
    VERSION: str = "1.0.0"
    

    # Database settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    DATABASE_URL: str = 'your_url'


    # Celery settings
    CELERY_BROKER_URL: str = 'your_url'
    CELERY_RESULT_BACKEND: str = 'your_backenn'

    #debug
    DEBUG: bool = False

    #LLM settings
    LLM_API_URL: str = "https://mock-llm-api.example.com/generate"
    LLM_API_KEY: str = 'krjvkjrtnkj'
    LLM_MODEL_NAME: str = "default-model"

    class Config:
        env_file = ".env"


settings = Settings()
