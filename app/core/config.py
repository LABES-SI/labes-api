from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "labes-api"

    db_user: str = Field(..., validation_alias="DB_USER")
    db_pass: str = Field(..., validation_alias="DB_PASS")
    db_host: str = Field(..., validation_alias="DB_HOST")
    db_port: int = Field(5432, validation_alias="DB_PORT")
    db_name: str = Field(..., validation_alias="DB_NAME")

    @property
    def warehouse_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
