from fastapi import Depends
from sqlmodel import Session, select

from backend.dependencies.connections import get_db_session_dependency
from backend.models import Clients, Clients_Addresses

def load_client_by_CNPJ(CNPJ: str, session: Session = Depends(get_db_session_dependency)):
    stmt = select(Clients).where(Clients.CNPJ == CNPJ)
    return session.exec(stmt).one_or_none()

def load_client_by_CPF(CPF: str, session: Session = Depends(get_db_session_dependency)):
    stmt = select(Clients).where(Clients.CPF == CPF)
    return session.exec(stmt).one_or_none()

def load_client_address(client: Client, session: Session = Depends(get_db_session_dependency)):
    stmt = select(Clients.id, Clients_Addresses).join(Clients_Addresses).where(Clients.id == client.id).order_by(Clients.id)
    return session.exec(stmt).first().one_or_none()
