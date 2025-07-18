from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlmodel import Session

from backend.dependencies.connections import get_db_session
from backend.services.infomgmt.clientsmgmt import (
    register_new_client,
    register_new_client_card,
    register_new_client_pix_key,
    load_client_by_CNPJ,
    load_client_by_CPF,
    load_client_address,
    load_client_pix_keys,
    load_client_cards,
)
from backend.routers.utils.input_checkers import (
    transform_document_to_digits,
    check_CNPJ_length,
    check_CPF_length,
    CNPJ_OFICIAL_LENGTH,
    CPF_OFICIAL_LENGTH,
)

clients_router = APIRouter(prefix='/clients', tags=['Client information'])

#* POST
@clients_router.post("/new")
def new_client(name: str, address: str, address_number: str, complement: str, district: str,
                    CNPJ: str = None, CPF: str = None, zip_code: str = None, CEP: str = None, active: bool = True,
                    session: Session = Depends(get_db_session)):
    if not CPF and not CNPJ:
        raise HTTPException(detail="Newbank's Clients operations needs CNPJ or CPF.", status_code=403)
    elif CPF and CNPJ: 
        raise HTTPException(detail="Newbank's Clients operations needs CNPJ or CPF. Please use only ONE document.", status_code=403)
    
    if not CEP and not zip_code:
        raise HTTPException(detail="Newbank's Clients needs CEP or Zip Code.", status_code=403)
    elif CEP and zip_code: 
        raise HTTPException(detail="Newbank's Clients operations needs CEP or Zip Code. Please use only ONE code.", status_code=403)


    if CNPJ:
        CNPJ = transform_document_to_digits(CNPJ, 'CNPJ')
    elif CPF:
        CPF = transform_document_to_digits(CPF, 'CPF')

    if CNPJ and not check_CNPJ_length(CNPJ):
        raise HTTPException(detail=f"CNPJ is not valid, please assure it's {CNPJ_OFICIAL_LENGTH} characters long.", status_code=400)
    if CPF and not check_CPF_length(CPF):
        raise HTTPException(detail=f"CPF is not valid, please assure it's {CPF_OFICIAL_LENGTH} characters long.", status_code=400)

    result: bool = register_new_client(CNPJ, CPF, name, address, address_number, complement,
                                    district, zip_code, CEP, active=active, session=session)

    if result:
        return {"result": "sucess"}
    else: return {"result": "failure"}

@clients_router.post("/new/card", summary="Register a new card for the client. The default card type is Phyisical, which is allowed 1 per client")
def new_client_card(CNPJ: str = None, CPF: str = None, cardType: str = "physical", session: Session = Depends(get_db_session)):
    if not CPF and not CNPJ:
        raise HTTPException(detail="Newbank's Clients operations needs CNPJ or CPF.", status_code=403)
    elif CPF and CNPJ: 
        raise HTTPException(detail="Newbank's Clients operations needs CNPJ or CPF. Please use only ONE document.", status_code=403)

    if CNPJ:
        CNPJ = transform_document_to_digits(CNPJ, 'CNPJ')
    elif CPF:
        CPF = transform_document_to_digits(CPF, 'CPF')

    if CNPJ and not check_CNPJ_length(CNPJ):
        raise HTTPException(detail=f"CNPJ is not valid, please assure it's {CNPJ_OFICIAL_LENGTH} characters long.", status_code=400)
    if CPF and not check_CPF_length(CPF):
        raise HTTPException(detail=f"CPF is not valid, please assure it's {CPF_OFICIAL_LENGTH} characters long.", status_code=400)

    result = register_new_client_card(session, CNPJ, CPF, cardType)
    
    if result:
        return {"result": "sucess"}
    else: return {"result": "failure"}

@clients_router.post("/new/pix", summary="Register a new Pix key for the client. The default key type is random. 1 type of key is allowed per client")
def new_client_pix_key(key: str, CNPJ: str = None, CPF: str = None, pixType: str = "random", session: Session = Depends(get_db_session)):
    if not CPF and not CNPJ:
        raise HTTPException(detail="Newbank's Clients operations needs CNPJ or CPF.", status_code=403)
    elif CPF and CNPJ: 
        raise HTTPException(detail="Newbank's Clients operations needs CNPJ or CPF. Please use only ONE document.", status_code=403)

    if CNPJ:
        CNPJ = transform_document_to_digits(CNPJ, 'CNPJ')
    elif CPF:
        CPF = transform_document_to_digits(CPF, 'CPF')

    if CNPJ and not check_CNPJ_length(CNPJ):
        raise HTTPException(detail=f"CNPJ is not valid, please assure it's {CNPJ_OFICIAL_LENGTH} characters long.", status_code=400)
    if CPF and not check_CPF_length(CPF):
        raise HTTPException(detail=f"CPF is not valid, please assure it's {CPF_OFICIAL_LENGTH} characters long.", status_code=400)

    result = register_new_client_pix_key(session, key, CNPJ, CPF, pixType)
    
    if result:
        return {"result": "sucess"}
    else: return {"result": "failure"}


#* GET
@clients_router.get("/load/CNPJ")
def get_client_with_CNPJ(CNPJ: str, session: Session = Depends(get_db_session)):
    CNPJ = transform_document_to_digits(CNPJ, 'CNPJ')

    if not check_CNPJ_length(CNPJ):
        raise HTTPException(detail=f"CNPJ is not valid, please assure it's {CNPJ_OFICIAL_LENGTH} characters long.", status_code=400)
    
    result = load_client_by_CNPJ(CNPJ=CNPJ, session=session)

    if result:
        return result
    else: raise HTTPException(detail="No client was found with this CNPJ.", status_code=404)

@clients_router.get("/load/CPF")
def get_client_with_CPF(CPF: str, session: Session = Depends(get_db_session)):
    CPF = transform_document_to_digits(CPF, 'CPF')

    if not check_CPF_length(CPF):
        raise HTTPException(detail=f"CPF is not valid, please assure it's {CPF_OFICIAL_LENGTH} characters long.", status_code=400)
    
    result = load_client_by_CPF(CPF=CPF, session=session)

    if result:
        return result
    else: raise HTTPException(detail="No client was found with this CPF.", status_code=404)

@clients_router.get("/load/address")
def get_client_address_with_CNPJ_or_CPF(CNPJ: str = None, CPF: str = None, session: Session = Depends(get_db_session)):
    if not CPF and not CNPJ:
        raise HTTPException(detail="Newbank's Clients operations needs CNPJ or CPF.", status_code=403)
    elif CPF and CNPJ: 
        raise HTTPException(detail="Newbank's Clients operations needs CNPJ or CPF. Please use only ONE document.", status_code=403)

    if CNPJ:
        CNPJ = transform_document_to_digits(CNPJ, 'CNPJ')
    elif CPF:
        CPF = transform_document_to_digits(CPF, 'CPF')

    if CNPJ and not check_CNPJ_length(CNPJ):
        raise HTTPException(detail=f"CNPJ is not valid, please assure it's {CNPJ_OFICIAL_LENGTH} characters long.", status_code=400)
    if CPF and not check_CPF_length(CPF):
        raise HTTPException(detail=f"CPF is not valid, please assure it's {CPF_OFICIAL_LENGTH} characters long.", status_code=400)
    
    result = load_client_address(CNPJ=CNPJ, CPF=CPF, session=session)

    if result:
        return result
    else: raise HTTPException(detail="No client address was found with this CNPJ.", status_code=404)

@clients_router.get("/load/cards")
def get_client_cards(CNPJ: str = None, CPF: str = None, type_card: str = None, session: Session = Depends(get_db_session)):
    if not CPF and not CNPJ:
        raise HTTPException(detail="Newbank's Clients operations needs CNPJ or CPF.", status_code=403)
    elif CPF and CNPJ: 
        raise HTTPException(detail="Newbank's Clients operations needs CNPJ or CPF. Please use only ONE document.", status_code=403)

    if CNPJ:
        CNPJ = transform_document_to_digits(CNPJ, 'CNPJ')
    elif CPF:
        CPF = transform_document_to_digits(CPF, 'CPF')

    if CNPJ and not check_CNPJ_length(CNPJ):
        raise HTTPException(detail=f"CNPJ is not valid, please assure it's {CNPJ_OFICIAL_LENGTH} characters long.", status_code=400)
    if CPF and not check_CPF_length(CPF):
        raise HTTPException(detail=f"CPF is not valid, please assure it's {CPF_OFICIAL_LENGTH} characters long.", status_code=400)

    result = load_client_cards(session, CNPJ, CPF, type_card)

    if result:
        return result
    else: raise HTTPException(detail="No client address was found with this CNPJ.", status_code=404)
    
@clients_router.get("/load/pix_key")
def get_client_pix_keys(CNPJ: str = None, CPF: str = None, type_pix: str = None, session: Session = Depends(get_db_session)):
    if not CPF and not CNPJ:
        raise HTTPException(detail="Newbank's Clients operations needs CNPJ or CPF.", status_code=403)
    elif CPF and CNPJ: 
        raise HTTPException(detail="Newbank's Clients operations needs CNPJ or CPF. Please use only ONE document.", status_code=403)

    if CNPJ:
        CNPJ = transform_document_to_digits(CNPJ, 'CNPJ')
    elif CPF:
        CPF = transform_document_to_digits(CPF, 'CPF')

    if CNPJ and not check_CNPJ_length(CNPJ):
        raise HTTPException(detail=f"CNPJ is not valid, please assure it's {CNPJ_OFICIAL_LENGTH} characters long.", status_code=400)
    if CPF and not check_CPF_length(CPF):
        raise HTTPException(detail=f"CPF is not valid, please assure it's {CPF_OFICIAL_LENGTH} characters long.", status_code=400)

    result = load_client_pix_keys(session, CNPJ, CPF, type_pix)

    if result:
        return result
    else: raise HTTPException(detail="No client address was found with this CNPJ.", status_code=404)

