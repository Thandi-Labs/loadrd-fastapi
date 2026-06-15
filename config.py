from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int = 20

    postgres_user: str
    postgres_password: str
    postgres_db: str

    # model_config = ConfigDict(extra='ignore', env_file='.env')

    class Config:
        env_file = ".env"


settings = Settings()
