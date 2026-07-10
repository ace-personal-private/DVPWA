from sqlmodel import SQLModel, create_engine

from app import models  # noqa: F401 -- ensures all tables are registered on metadata
from app.config import settings

engine = create_engine(settings.database_url, echo=True)


def create_db_and_tables() -> None:
    """Create the database and tables."""
    SQLModel.metadata.create_all(engine)
