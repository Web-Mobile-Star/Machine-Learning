from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.schema import Table

from ml_service.helper import SingletonMeta


class SessionMakerSingleton(metaclass=SingletonMeta):
    def __init__(
        self,
        engine=None,
        input_table_model: Table = None,
        output_table_model: Table = None,
    ):
        assert engine is not None
        assert input_table_model is not None
        assert output_table_model is not None
        input_table_model.metadata.create_all(bind=engine)
        output_table_model.metadata.create_all(bind=engine)
        self.sessionmaker = sessionmaker(
            autocommit=False, autoflush=False, bind=engine
        )


Base = declarative_base()
