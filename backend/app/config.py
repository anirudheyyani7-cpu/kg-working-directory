from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = "password"
    upstash_redis_rest_url: str = ""
    upstash_redis_rest_token: str = ""
    anthropic_api_key: str = ""
    environment: str = "development"
    log_level: str = "INFO"
    ingest_interval_hours: int = 4
    confidence_threshold: float = 0.75


settings = Settings()
