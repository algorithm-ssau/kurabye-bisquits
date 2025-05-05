from logging import INFO, Logger, basicConfig
from logging.handlers import TimedRotatingFileHandler

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


class LoggingSettings(ModelConfig):
    # Documentation: https://docs.python.org/3/library/logging.html
    log_directory: str = Field(default="/logs", validation_alias="LOG_DIRECTORY")
    date_format: str = Field(default="%Y-%m-%d %H:%M:%S", validation_alias="DATE_FORMAT")
    log_format: str = Field(
        default="[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-7s - %(message)s",
        validation_alias="LOG_FORMAT",
    )
    log_roating: str = Field(default="midnight", validation_alias="LOG_ROATING")
    backup_count: int = Field(
        default=30,
        validation_alias="BACKUP_COUNT",
        description="Interval of backup/roating logs. Default 30 midnites. 31st log will ovverides the first log.",
    )
    utc: bool = Field(default=True, validation_alias="LOG_UTC")

    def configure_logging(
        self,
        logger: Logger,
        filename: str,
        level=INFO,
    ):
        handler = TimedRotatingFileHandler(
            filename=f"{self.log_directory}/log_{filename}",
            when=self.log_roating,
            backupCount=self.backup_count,
            utc=self.utc,
        )
        logger.addHandler(handler)

        basicConfig(
            level=level,
            filename=f"{self.log_directory}/log_{filename}",
            filemode="at",
            datefmt=self.date_format,
            format=self.log_format,
        )


# create config instances
host_settings = HostSettings()
auth_settings = AuthSettings()
db_settings = DBSettings()
log_setting = LoggingSettings()
