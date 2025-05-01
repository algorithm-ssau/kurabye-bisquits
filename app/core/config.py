from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings.main import SettingsConfigDict


class ModelConfig(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        # ignore extra vars in the env file
        extra="ignore",
    )


class HostSettings(ModelConfig):
    host: str = Field(default="localhost", validation_alias="APP_HOST")
    port: int = Field(default=8000, validation_alias="APP_PORT")


class AuthSettings(ModelConfig):
    secret_key: str = Field(default="my-cool-secret-key", validation_alias="APP_SECRET_KEY")
    algorithm: str = Field(default="HS256", validation_alias="APP_ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, validation_alias="APP_ACCESS_TOKEN_EXPIRE_MINUTES")


# create config instances
host_settings = HostSettings()
auth_settings = AuthSettings()
