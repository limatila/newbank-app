from fastapi import Depends
from sqlmodel import Session, select

from backend.dependencies.connections import get_db_session_dependency
from backend.models import Emitters

def register_new_emitter(CNPJ: str, name: str, active: bool = True,
                        session: Session = Depends(get_db_session_dependency)):

    newEmitter = Emitters(CNPJ=CNPJ, name=name, active=active)
    session.add(newEmitter)
    session.commit()

#Getters
def load_emitter_by_CNPJ(CNPJ: str, session: Session = Depends(get_db_session_dependency)):
    stmt = select(Emitters).where(Emitters.CNPJ == CNPJ)
    return session.exec(stmt).one_or_none()