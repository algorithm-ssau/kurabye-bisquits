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


class DBSettings(ModelConfig):
    db_type: str = Field(default="postgresql", validation_alias="DB_TYPE")
    db_host: str = Field(default="localhost", validation_alias="DB_HOST")
    db_port: str = Field(default="5432", validation_alias="DB_PORT")
    db_driver: str = Field(default="asyncpg", validation_alias="DB_DRIVER")
    db_user: str = Field(default="root", validation_alias="DB_USER")
    db_user_password: str = Field(default="root", validation_alias="DB_USER_PASSWORD")
    db_name: str = Field(default="db", validation_alias="DB_NAME")
    db_echo: bool = Field(default=False, validation_alias="DB_ECHO")

    @property
    def db_url(self):
        return (
            f"{self.db_type}+{self.db_driver}://"
            f"{self.db_user}:{self.db_user_password}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )


# create config instances
host_settings = HostSettings()
auth_settings = AuthSettings()
db_settings = DBSettings()
