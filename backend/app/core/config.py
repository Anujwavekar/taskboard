from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    client_url: str = "http://localhost:5173"
    jwt_expire_days: int = 7

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()