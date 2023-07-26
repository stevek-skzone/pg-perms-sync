from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """
    Configuration settings for the application.

    Environment variables can be used to override the default values.
    """

    model_config = SettingsConfigDict(env_prefix="", case_sensitive=False)

    POSTGREST_URL: str = "http://localhost:3000"
    ENTITLEMENT_CACHE_SERVER: str = "http://localhost:8080"
    LOGSTASH_ADDRESS: str = "localhost:5000"
    LISTEN_PORT: int = 8000
    DEBUG: bool = False
    RELOAD: bool = False
    WORKERS: int = 1


config = Config()
