from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlmodel import Session

from backend.dependencies.connections import get_db_session
from backend.services.infomgmt.emittersmgmt import (
    register_new_emitter,
    load_emitter_by_CNPJ,
    change_emitter_active_status,
)
from backend.routers.utils.input_checkers import (
    transform_document_to_digits,
    check_CNPJ_length,
    CNPJ_OFICIAL_LENGTH,
)

emitters_router = APIRouter(prefix='/emitters', tags=['Emitter information'])

#* POST
@emitters_router.post("/new")
def new_client(CNPJ: str, name: str, active: bool = True, session: Session = Depends(get_db_session)):
    CNPJ = transform_document_to_digits(CNPJ, 'CNPJ')

    if not check_CNPJ_length(CNPJ):
        raise HTTPException(detail=f"CNPJ is not valid, please assure it's {CNPJ_OFICIAL_LENGTH} characters long.", status_code=400)

    result: bool = register_new_emitter(CNPJ, name, active=active, session=session)

    if result:
        return {"result": "sucess"}
    else: return {"result": "failure"}


#* GET
@emitters_router.get("/load/CNPJ")
def get_emitter_by_CNPJ(CNPJ: str, session: Session = Depends(get_db_session)):
    CNPJ = transform_document_to_digits(CNPJ, 'CNPJ')

    if not check_CNPJ_length(CNPJ):
        raise HTTPException(detail=f"CNPJ is not valid, please assure it's {CNPJ_OFICIAL_LENGTH} characters long.", status_code=400)

    result: bool = load_emitter_by_CNPJ(CNPJ, session)

    if result:
        return result
    else: raise HTTPException(detail="No emitter was found with this CNPJ.", status_code=404)


#* PUT
@emitters_router.put("/alter/status")
def get_emitter_by_CNPJ(newStatus: bool, CNPJ: str, session: Session = Depends(get_db_session)):
    CNPJ = transform_document_to_digits(CNPJ, 'CNPJ')

    if not check_CNPJ_length(CNPJ):
        raise HTTPException(detail=f"CNPJ is not valid, please assure it's {CNPJ_OFICIAL_LENGTH} characters long.", status_code=400)

    return change_emitter_active_status(session, newStatus, CNPJ)