from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlmodel import Session

from backend.dependencies.connections import get_db_session
from backend.services.infomgmt.emittersmgmt import (
    register_new_emitter,
    load_emitter_by_CNPJ,
)
from backend.routers.utils.input_checkers import (
    transform_document_to_digits,
    check_CNPJ_length,
    CNPJ_OFICIAL_LENGTH,
)

emitters_router = APIRouter(prefix='/emitters', tags=['Emitter information'])

#POST
@emitters_router.post("/new")
def new_client(CNPJ: str, name: str, active: bool = True, session: Session = Depends(get_db_session)):
    CNPJ = transform_document_to_digits(CNPJ, 'CNPJ')

    if not check_CNPJ_length(CNPJ):
        raise HTTPException(detail=f"CNPJ is not valid, please assure it's {CNPJ_OFICIAL_LENGTH} characters long.", status_code=400)

    result: bool = register_new_emitter(CNPJ, name, active=active, session=session)

    if result:
        return {"result": "sucess"}
    else: return {"result": "failure"}

#GET
@emitters_router.get("/load/CNPJ/{CNPJ_number}")
def get_emitter_by_CNPJ(CNPJ_number: str, session: Session = Depends(get_db_session)):
    CNPJ_number = transform_document_to_digits(CNPJ_number, 'CNPJ')

    if not check_CNPJ_length(CNPJ_number):
        raise HTTPException(detail=f"CNPJ is not valid, please assure it's {CNPJ_OFICIAL_LENGTH} characters long.", status_code=400)

    result: bool = load_emitter_by_CNPJ(CNPJ_number, session)

    if result:
        return result
    else: raise HTTPException(detail="No emitter was found with this CNPJ.", status_code=404)