from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from backend.models import Emitters

# Create
def register_new_emitter(CNPJ: str, name: str, session: Session, active: bool = True) -> bool: 
    try:
        newEmitter = Emitters(CNPJ=CNPJ, name=name, active=active)
        session.add(newEmitter)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(detail="Emitter with that CNPJ already exists", status_code=409)

    return True if newEmitter else False


# Getters
def load_emitter_by_CNPJ(CNPJ: str, session: Session):
    stmt = select(Emitters).where(Emitters.CNPJ == CNPJ)
    return session.exec(stmt).one_or_none()