from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError 

from backend.models import Clients, Client_Addresses

# Create
def register_new_client(CNPJ: str, CPF: str, name: str, address: str, address_number: str, complement: str, 
                        district: str, zip_code: str, CEP: str, session: Session, active: bool = True):    
    #TODO: new_credit = generate_new_credit(CPF, CNPJ)  #performs calculation for client's new credit

    #find duplicate
    stmt_address = select(Client_Addresses).where(
            Client_Addresses.address == address,
            Client_Addresses.number == address_number,
            Client_Addresses.complement == complement,
            Client_Addresses.district == district,
            Client_Addresses.zip_code == zip_code,
            Client_Addresses.CEP == CEP,
        )
    existing_address = session.exec(stmt_address).first()

    if existing_address:
        newAddress = existing_address
    else:
        newAddress = Client_Addresses(address=address, number=address_number, complement=complement, district=district, zip_code=zip_code, CEP=CEP)
        session.add(newAddress)
        session.commit()

    try:
        newClient = Clients(CPF=CPF, CNPJ=CNPJ, name=name, active=active, FK_idAddress=newAddress.id)
        session.add(newClient)#finally
        session.commit() #TODO: move
    except IntegrityError:
        session.rollback()
        raise HTTPException(detail=f"Client with that {"CNPJ" if CNPJ else "CPF"} already exists in database.", status_code=409)

    if newAddress and newClient:
        return True
    else: False


# Getters
def load_client_by_CNPJ(CNPJ: str, session: Session):
    stmt = select(Clients).where(Clients.CNPJ == CNPJ)
    return session.exec(stmt).one_or_none()

def load_client_by_CPF(CPF: str, session: Session):
    stmt = select(Clients).where(Clients.CPF == CPF)
    return session.exec(stmt).one_or_none()

def load_client_address(CPF: str, CNPJ: str, session: Session):
    if CNPJ:
       client: Clients = load_client_by_CNPJ(CNPJ)
    elif CPF: 
       client: Clients = load_client_by_CPF(CPF)
    else: raise Exception("Address search needs CNPJ or CPF to work.")

    if not client: raise HTTPException(detail="No client was found when searching address.", status_code=404)

    stmt = select(Clients.id, Client_Addresses).join(Client_Addresses) \
                    .where(Client_Addresses.client.id == client.id).order_by(Client_Addresses.id)
    result = session.exec(stmt).first().one_or_none()

    #interpreting before deliver
    if isinstance(result, tuple):
        result = {
            "client_id": result[0],
            "client_address": result[1]
        }

    return result