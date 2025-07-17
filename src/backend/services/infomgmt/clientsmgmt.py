from fastapi import HTTPException
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError 

from backend.models import Clients, Client_Addresses, Cards, Pix_keys
from backend.models.utils.enums import TypeCard, TypePixKey
from .infoGenerators import (
    generate_new_credit_balance,
    generate_new_card_digits,
    generate_new_card_CVV_code,
    generate_new_card_date_expiration,
)


# Create
def register_new_client(CNPJ: str, CPF: str, name: str, address: str, address_number: str, complement: str, 
                        district: str, zip_code: str, CEP: str, session: Session, active: bool = True) -> bool:    
    
    #find duplicate address
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

    #register client
    newCredit = generate_new_credit_balance(CNPJ, CPF)
    try:
        newClient = Clients(CPF=CPF, CNPJ=CNPJ, name=name, active=active, credit_balance=newCredit, FK_idAddress=newAddress.id)
        session.add(newClient)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(detail=f"Client with that {"CNPJ" if CNPJ else "CPF"} already exists in database.", status_code=409)

    return True if (newAddress and newClient) else False

def register_new_client_card(session: Session, CNPJ: str = None, CPF: str = None, cardType: str = "physical") -> bool:
    if CNPJ:
       client: Clients = load_client_by_CNPJ(CNPJ, session)
    elif CPF: 
       client: Clients = load_client_by_CPF(CPF, session)
    else: raise Exception("Card registration needs CNPJ or CPF to work.")

    if not client: raise HTTPException(detail="No client was found when searching address.", status_code=404)

    newDigits = generate_new_card_digits()
    newExpiration = generate_new_card_date_expiration()
    newCVV_code = generate_new_card_CVV_code()
    attributedType = TypeCard.from_str(cardType) #! what about a wrong type insertion?

    #TODO add limit for client cards

    #verify another card with generated data
    stmt = select(Cards) \
            .where(Cards.digits == newDigits) \
            .where(Cards.date_expires == newExpiration) \
            .where(Cards.CVV_code == newCVV_code)
    cardExists = session.exec(stmt).one_or_none()

    if cardExists:
        result = register_new_client_card(session, CNPJ, CPF, cardType) #recursive, break if has been sucessfull
        return True if result else False
    else:
        newCard = Cards(digits=newDigits, date_expires=newExpiration, CVV_code=newCVV_code, FK_idCliente=client.id, type_card=attributedType)
        session.add(newCard)
        session.commit()

    return True if (newCard or result) else False

def register_new_client_pix_key(session: Session, key: str, CNPJ: str = None, CPF: str = None, pixType: str = "random") -> bool:
    if CNPJ:
       client: Clients = load_client_by_CNPJ(CNPJ, session)
    elif CPF: 
       client: Clients = load_client_by_CPF(CPF, session)
    else: raise Exception("Pix Key registration needs CNPJ or CPF to work.")

    if not client: raise HTTPException(detail="No client was found when searching address.", status_code=404)

    attributedType = TypePixKey.from_str(pixType)

    #verify no key with same type exists for the client (1 type of each per client)
    stmt = select(Pix_keys) \
            .join(Clients, Clients.id == Pix_keys.FK_idCliente) \
            .where(Pix_keys.type_key == attributedType)
    keyTypeExists = session.exec(stmt).one_or_none()
    
    if keyTypeExists:
        raise HTTPException(detail=f"Pix with the type of key \'{attributedType.title()}\' already exists in database for this client.", status_code=409)

    newKey = Pix_keys(type_key=attributedType, key=key, FK_idCliente=client.id)
    session.add(newKey)
    session.commit()

    return True if newKey else False

# Getters
def load_client_by_CNPJ(CNPJ: str, session: Session):
    stmt = select(Clients).where(Clients.CNPJ == CNPJ)
    return session.exec(stmt).one_or_none()

def load_client_by_CPF(CPF: str, session: Session):
    stmt = select(Clients).where(Clients.CPF == CPF)
    return session.exec(stmt).one_or_none()

def load_client_address(session: Session, CPF: str = None, CNPJ: str = None) -> dict[str, int | Client_Addresses]: #todo: change position -> dict[str, int]s
    if CNPJ:
       client: Clients = load_client_by_CNPJ(CNPJ, session)
    elif CPF: 
       client: Clients = load_client_by_CPF(CPF, session)
    else: raise Exception("Address search needs CNPJ or CPF to work.")

    if not client: raise HTTPException(detail="No client was found when searching address.", status_code=404)

    stmt = select(Client_Addresses).join(Clients) \
                    .where(Clients.id == client.id).order_by(Client_Addresses.id)
    result = session.exec(stmt).one_or_none()

    #interpreting before deliver
    return {
            "client_id": client.id,
            "client_address": result
        }

def load_client_card(session: Session, CPF: str = None, CNPJ: str = None, cardType: str = "physical") -> dict[str, int | Cards]:
    if CNPJ:
       client: Clients = load_client_by_CNPJ(CNPJ, session)
    elif CPF: 
       client: Clients = load_client_by_CPF(CPF, session)
    else: raise Exception("Address search needs CNPJ or CPF to work.")

    if not client: raise HTTPException(detail="No client was found when searching address.", status_code=404)

    attributedType = TypeCard.from_str(cardType)

    stmt = select(Cards) \
            .join(Clients, Clients.id == Cards.FK_idCliente) \
            .where(Cards.type_key == attributedType)
    result = session.exec(stmt).one_or_none()

    if not result: raise HTTPException(detail="No card was found when searching address.", status_code=404)

    #interpreting before deliver
    return {
            "client_id": client.id,
            "client_pix_key": result
        }

def load_client_pix_key(session: Session, CPF: str = None, CNPJ: str = None, pixType: str = "random") -> dict[str, int | Pix_keys]:
    if CNPJ:
       client: Clients = load_client_by_CNPJ(CNPJ, session)
    elif CPF: 
       client: Clients = load_client_by_CPF(CPF, session)
    else: raise Exception("Address search needs CNPJ or CPF to work.")

    if not client: raise HTTPException(detail="No client was found when searching address.", status_code=404)
    
    attributedType = TypePixKey.from_str(pixType)

    stmt = select(Pix_keys) \
            .join(Clients, Clients.id == Pix_keys.FK_idCliente) \
            .where(Pix_keys.type_key == attributedType)
    result = session.exec(stmt).one_or_none()

    if not result: raise HTTPException(detail="No card was found when searching address.", status_code=404)

    #interpreting before deliver
    return {
            "client_id": client.id,
            "client_pix_key": result
        }


# Alters #TODO
def change_client_active_status(session: Session, newStatus: bool, CPF: str = None, CNPJ: str = None): ...
def change_client_address(session: Session, newAddress: str, CPF: str = None, CNPJ: str = None): ...
def deactivate_client_card(session: Session, newStatus: bool, CPF: str = None, CNPJ: str = None): ...
def delete_client_pix_key(session: Session, newStatus: bool, CPF: str = None, CNPJ: str = None): ...
