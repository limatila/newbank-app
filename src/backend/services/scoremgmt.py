from fastapi import Depends
from sqlmodel import Session, select

from backend.dependencies.connections import get_db_session
from backend.models import Clients

def load_client_by_CNPJ(CNPJ: str, session: Session = Depends(get_db_session)):
    stmt = select(Clients).where(Clients.CNPJ == CNPJ)
    return session.exec(stmt).one_or_none()

