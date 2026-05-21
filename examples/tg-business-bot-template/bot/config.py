from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    database_url: str
    sales_calendar_url: str = "https://example.com/consultation"
    sales_phone: str = ""
    followup_enabled: bool = True
    followup_poll_seconds: int = 60
    followup_test_mode: bool = False

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
