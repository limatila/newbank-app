from datetime import datetime
from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from backend.models import Emitters

#* Create
def register_new_emitter(CNPJ: str, name: str, session: Session, active: bool = True) -> bool: 
    try:
        newEmitter = Emitters(CNPJ=CNPJ, name=name, active=active)
        session.add(newEmitter)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(detail="Emitter with that CNPJ already exists", status_code=409)

    return True if newEmitter else False


#* Getters
def load_emitter_by_CNPJ(CNPJ: str, session: Session):
    stmt = select(Emitters).where(Emitters.CNPJ == CNPJ)
    result = session.exec(stmt).one_or_none()
    if not result: raise HTTPException(detail="No emitter was found for the sent document.", status_code=404)

    return result


#* Alters
def change_emitter_active_status(session: Session, newStatus: bool, CNPJ: str):
    emitter: Emitters = load_emitter_by_CNPJ(CNPJ, session)

    wasDeactivated, wasEqualStatus = (False, False)

    #modeling response
    if newStatus == emitter.active:
        wasEqualStatus = True

    #alter it
    if not wasEqualStatus:
        emitter.active = newStatus
    #adding deactivation date
    if newStatus == False:
        newDeactivationDate = datetime.now() 
        emitter.date_deactivated = newDeactivationDate
        wasDeactivated = True

    if not wasEqualStatus:
        session.add(emitter)
        session.commit()

    result = {
        "result": "sucess",
    }
    if wasEqualStatus: result.update({"detail": f"Emitter was already at state {'active' if newStatus else 'deactivated'}"})
    if wasDeactivated: result.update({"date_deactivated": emitter.date_deactivated})

    return result
