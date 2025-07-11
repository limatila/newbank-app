from fastapi import Depends
from sqlmodel import Session, select

from backend.dependencies.connections import get_db_session_dependency

def get_client_by_CPF(CPF: str, session: Session = Depends(get_db_session_dependency)):
    ...
