from os import environ

# from pydantic import BaseSettings  # pylint: disable=no-name-in-module


class Config:
    """
    Configuration settings for the application.

    Environment variables can be used to override the default values.
    """

    POSTGREST_URL: str = environ.get("POSTGREST_URL", "http://localhost:3000")
    ENTITLEMENT_CACHE_SERVER: str = environ.get(
        "ENTITLEMENT_CACHE_SERVER", "http://localhost:8080"
    )
    LOGSTASH_ADDRESS: str = environ.get("LOGSTASH_ADDRESS", "localhost:5000")
    LISTEN_PORT: int = int(environ.get("LISTEN_PORT", "8000"))
    DEBUG: bool = environ.get("DEBUG", "false").lower() == "true"
    RELOAD: bool = environ.get("RELOAD", "false").lower() == "true"
    WORKERS: int = int(environ.get("WORKERS", "1"))
