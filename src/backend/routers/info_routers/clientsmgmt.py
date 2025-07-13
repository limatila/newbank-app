from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlmodel import Session

from backend.dependencies.connections import get_db_session_dependency
from backend.services.infomgmt.clientsmgmt import (
    register_new_client,
    load_client_by_CNPJ,
    load_client_by_CPF,
    load_client_address,
)
from backend.routers.utils.input_checkers import (
    check_CNPJ_length,
    check_CPF_length,
    CNPJ_OFICIAL_LENGTH,
    CPF_OFICIAL_LENGTH,
)

clients_router = APIRouter(prefix='/clients', tags=['Client information'])

#POST
@clients_router.post("/new")
def new_client(name: str, address: str, address_number: str, complement: str, district: str,
                    CNPJ: str = None, CPF: str = None, zip_code: str = None, CEP: str = None, active: bool = True,
                    session: Session = Depends(get_db_session_dependency)):
    if not CPF and not CNPJ:
        raise HTTPException(detail="Newbank's Clients needs CNPJ or CPF.", status_code=403)
    if not CEP and not zip_code:
        raise HTTPException(detail="Newbank's Clients needs CEP or Zip Code.", status_code=403)

    if CNPJ and not check_CNPJ_length(CNPJ):
        raise HTTPException(detail=f"CNPJ is not valid, please assure it's {CNPJ_OFICIAL_LENGTH} characters long.", status_code=400)
    if CPF and not check_CPF_length(CPF):
        raise HTTPException(detail=f"CPF is not valid, please assure it's {CPF_OFICIAL_LENGTH} characters long.", status_code=400)

    result: bool = register_new_client(CNPJ, CPF, name, address, address_number, complement,
                                    district, zip_code, CEP, active=active, session=session)

    if result:
        return {"result": "sucess"}
    else: return {"result": "failure"}


#GET
@clients_router.get("/load/CNPJ/{CNPJ_number}")
def get_client_with_CNPJ(CNPJ_number: str, session: Session = Depends(get_db_session_dependency)):
    if not check_CNPJ_length(CNPJ_number):
        raise HTTPException(detail=f"CNPJ is not valid, please assure it's {CNPJ_OFICIAL_LENGTH} characters long.", status_code=400)
    
    result = load_client_by_CNPJ(CNPJ_number, session)

    if result:
        return result
    else: raise HTTPException(detail="No client was found with this CNPJ.", status_code=404)

@clients_router.get("/load/CPF/{CPF_number}")
def get_client_with_CPF(CPF_number: str, session: Session = Depends(get_db_session_dependency)):
    if not check_CPF_length(CPF_number):
        raise HTTPException(detail=f"CPF is not valid, please assure it's {CPF_OFICIAL_LENGTH} characters long.", status_code=400)
    
    result = load_client_by_CPF(CPF_number, session)

    if result:
        return result
    else: raise HTTPException(detail="No client was found with this CPF.", status_code=404)

@clients_router.get("/load-address/CNPJ/{CNPJ_number}")
def get_client_address_with_CNPJ(CNPJ_number: str, session: Session = Depends(get_db_session_dependency)):
    if not check_CNPJ_length(CNPJ_number):
        raise HTTPException(detail=f"CNPJ is not valid, please assure it's {CNPJ_OFICIAL_LENGTH} characters long.", status_code=400)
    
    result = load_client_address(CNPJ=CNPJ_number, session=session)

    if result:
        return result
    else: raise HTTPException(detail="No client address was found with this CNPJ.", status_code=404)

@clients_router.get("/load-address/CPF/{CPF_number}")
def get_client_address_with_CPF(CPF_number: str, session: Session = Depends(get_db_session_dependency)):
    if not check_CPF_length(CPF_number):
        raise HTTPException(detail=f"CPF is not valid, please assure it's {CPF_OFICIAL_LENGTH} characters long.", status_code=400)
    
    result = load_client_address(CPF=CPF_number, session=session)

    if result:
        return result
    else: raise HTTPException(detail="No client address was found with this CPF.", status_code=404)