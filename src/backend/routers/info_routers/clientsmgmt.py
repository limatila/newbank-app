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

    if CNPJ and len(CNPJ) != 14:
        raise HTTPException(detail="CNPJ is not valid, please assure it's 14 characters long.", status_code=400)
    if CPF and len(CPF) != 11:
        raise HTTPException(detail="CPF is not valid, please assure it's 11 characters long.", status_code=400)

    result = register_new_client(CPF, CNPJ, name, address, address_number, complement,
                                    district, zip_code, CEP, session=session)

    if result:
        return {"result": "sucess"}
    else: return {"result": "failure"}

#GET
@clients_router.get("/load/CNPJ/{CNPJ_number}")
def get_client_with_CNPJ(CNPJ_number: str, session: Session = Depends(get_db_session_dependency)):
    result = load_client_by_CNPJ(CNPJ_number, session)

    if result:
        return result
    else: raise HTTPException(detail="No client was found with this CNPJ.", status_code=404)

@clients_router.get("/load/CPF/{CPF_number}")
def get_client_with_CPF(CPF_number: str, session: Session = Depends(get_db_session_dependency)):
    result = load_client_by_CPF(CPF_number, session)

    if result:
        return result
    else: raise HTTPException(detail="No client was found with this CPF.", status_code=404)

@clients_router.get("/load-address/CNPJ/{CNPJ_number}")
def get_client_address_with_CNPJ(CNPJ_number: str, session: Session = Depends(get_db_session_dependency)):
    result = load_client_address(CNPJ=CNPJ_number, session=session)

    if result:
        return result
    else: raise HTTPException(detail="No client address was found with this CNPJ.", status_code=404)

@clients_router.get("/load-address/CPF/{CPF_number}")
def get_client_address_with_CPF(CPF_number: str, session: Session = Depends(get_db_session_dependency)):
    result = load_client_address(CPF=CPF_number, session=session)

    if result:
        return result
    else: raise HTTPException(detail="No client address was found with this CPF.", status_code=404)