from logging import INFO, Filter, Formatter, Logger, basicConfig, getLogger
from logging.handlers import TimedRotatingFileHandler
from os import mkdir, path

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings.main import SettingsConfigDict

from core.logging.filters import ColorFilter, SensitiveWordsFilter


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
    log_directory: str = Field(
        default="logs", validation_alias="LOG_DIRECTORY"
    )  # Изменен путь по умолчанию на относительный
    date_format: str = Field(default="%Y-%m-%d %H:%M:%S", validation_alias="DATE_FORMAT")
    log_format: str = Field(
        # Используем %(name) вместо %(module) для отображения имени логгера
        default="[%(asctime)s.%(msecs)03d] %(name)-30s:%(lineno)-3d %(levelname)-7s - %(message)s",
        validation_alias="LOG_FORMAT",
    )
    log_roating: str = Field(default="midnight", validation_alias="LOG_ROATING")
    backup_count: int = Field(
        default=30,
        validation_alias="BACKUP_COUNT",
        description="Interval of backup/roating logs. Default 30 midnights. 31st log will ovverides the first log.",
    )
    utc: bool = Field(default=True, validation_alias="LOG_UTC")
    # Добавим уровень логирования в настройки

    def get_configure_logging(self, filename: str, log_level=INFO) -> Logger:
        logger = getLogger(filename)

        if logger.hasHandlers():
            # we don't need to configurate logger if it already exists and configurated
            return logger

        logger.setLevel(log_level)

        try:
            if not path.isdir(self.log_directory):
                mkdir(self.log_directory)
        except OSError as error:
            logger.error("Не удалось создать директорию логов %r: %s", self.log_directory, error)

        log_formatter = Formatter(fmt=self.log_format, datefmt=self.date_format)

        safe_filename = filename.replace(".", "_") + ".log"
        log_file_path = path.join(self.log_directory, safe_filename)

        try:
            handler = TimedRotatingFileHandler(
                filename=log_file_path,
                when=self.log_roating,
                backupCount=self.backup_count,
                utc=self.utc,
                encoding="utf-8",
            )
            handler.setFormatter(log_formatter)
            handler.setLevel(log_level)

            # use this filter if you want see the logs in the console
            # logger.addFilter(ColorFilter())  # noqa: ERA001
            logger.addFilter(SensitiveWordsFilter())

            logger.addHandler(handler)

            logger.debug(
                "Logger %r successfuly configurated. Logger level: %s. Logger file: %r",
                filename,
                log_level,
                log_file_path,
            )

        except Exception as error:
            logger.error(
                "The error is ocured during the logger configuration. Logger %r: %s",
                logger,
                error,
            )
        return logger


# create config instances
host_settings = HostSettings()
auth_settings = AuthSettings()
db_settings = DBSettings()
log_setting = LoggingSettings()
