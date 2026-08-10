from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/ca_firm_mis"
    api_title: str = "CA Firm MIS API"
    api_version: str = "1.0.0"
    api_description: str = "Management Information System for CA Firm Compliance Tracking"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
