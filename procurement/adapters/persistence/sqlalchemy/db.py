from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from procurement.config.settings import DATABASE_URL


class Base(DeclarativeBase):
    pass


engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {},
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    from procurement.adapters.persistence.sqlalchemy import models  # noqa: F401

    Base.metadata.create_all(engine)
