import os
from typing import Dict, Type

from sqlalchemy.engine import create_engine


class PostgresEnvironment(object):
    DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")
    USER = os.environ.get("POSTGRES_USER")
    PASSWORD = os.environ.get("POSTGRES_PASSWORD")
    HOST = os.environ.get("POSTGRES_HOST")
    PORT = os.environ.get("POSTGRES_PORT")


def table_name_to_class_name(table_name: str) -> str:
    return table_name.replace("_", " ").title().replace(" ", "")


def postgres_connection_from_env() -> str:
    if PostgresEnvironment.DB_CONNECTION_STRING is not None:
        return PostgresEnvironment.DB_CONNECTION_STRING
    return (
        f"postgresql://{PostgresEnvironment.USER}:"
        f"{PostgresEnvironment.PASSWORD}@{PostgresEnvironment.HOST}:"
        f"{PostgresEnvironment.PORT}/{PostgresEnvironment.DATABASE_NAME}"
    )


def engine_from_env():
    return create_engine(postgres_connection_from_env(), echo=True)


class SingletonMeta(type):
    _instances: Dict[Type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[cls]
