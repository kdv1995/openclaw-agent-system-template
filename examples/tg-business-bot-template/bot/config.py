from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str
    database_url: str
    sales_calendar_url: str = "https://example.com/consultation"
    sales_phone: str = ""
    admin_telegram_ids: str = ""
    followup_enabled: bool = True
    followup_poll_seconds: int = 60
    followup_test_mode: bool = False
    crm_api_enabled: bool = True
    crm_api_host: str = "0.0.0.0"
    crm_api_port: int = 8000
    crm_api_key: str = ""
    sendpulse_crm_enabled: bool = False
    sendpulse_api_key: str = ""
    sendpulse_responsible_id: str = ""
    sendpulse_pipeline_id: str = ""
    sendpulse_step_id: str = ""
    sendpulse_deal_price: float = 0
    sendpulse_deal_currency: str = "UAH"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
