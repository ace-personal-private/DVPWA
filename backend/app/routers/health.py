from fastapi import APIRouter
from sqlmodel import Session, select

from app.database import engine

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    # ping the db with "SELECT 1" to check if the database is reachable
    with Session(engine) as session:
        statement = select(1)
        result = session.exec(statement)
        return {"status": "ok", "db_status": result.first() is not None}
