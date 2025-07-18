from sqlmodel import Sequence
from fastapi import HTTPException
from sqlmodel import Session, func, select
from sqlalchemy.exc import IntegrityError 

from backend.models import Clients, Client_Addresses, Client_Cards, Client_Pix_keys
from backend.models.utils.enums import TypeCard, TypePixKey
from .infoGenerators import (
    generate_new_credit_balance,
    generate_new_card_digits,
    generate_new_card_CVV_code,
    generate_new_card_date_expiration,
    generate_random_pix_key,
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

def register_new_client_card(session: Session, CNPJ: str = None, CPF: str = None, type_card: str = "physical", __recursion_flag: int = 0) -> bool:
    if CNPJ:
       client: Clients = load_client_by_CNPJ(CNPJ, session)
    elif CPF: 
       client: Clients = load_client_by_CPF(CPF, session)
    else: raise Exception("Card registration needs CNPJ or CPF to work.")

    if not client: raise HTTPException(detail="No client was found for the sent document.", status_code=404)

    newDigits = generate_new_card_digits()
    newExpiration = generate_new_card_date_expiration()
    newCVV_code = generate_new_card_CVV_code()

    try:
        attributedType = TypeCard.from_str(type_card)
    except ValueError:
        raise HTTPException(detail="No type of key is associated to the sent pix type.", status_code=404)


    #limit card quantity(1 phyisical, 5 virtual -- per client)
    stmt = select(func.count()).select_from(Client_Cards) \
            .join(Clients, Clients.id == Client_Cards.FK_idClient) \
            .where(Clients.id == client.id) \
            .where(Client_Cards.type_card == attributedType)
    countCards: int | None = session.exec(stmt).one_or_none()
    if countCards == None: countCards = 0

    if ((attributedType == TypeCard.PHYSICAL) and (countCards >= 1)) \
        or ((attributedType == TypeCard.VIRTUAL) and (countCards >= 5)):
        raise HTTPException(detail=f"The client already has too many cards of type {attributedType.title()}", status_code=409)

    #make sure card does not already exists
    stmt = select(Client_Cards) \
            .where(Client_Cards.digits == newDigits) \
            .where(Client_Cards.date_expires == newExpiration) \
            .where(Client_Cards.CVV_code == newCVV_code)
    cardExists = session.exec(stmt).one_or_none()

    if cardExists:
        result = None
        if __recursion_flag < 10: result = register_new_client_card(session, CNPJ, CPF, type_card, __recursion_flag=(__recursion_flag + 1)) #recursive, limited at ten tries
        return True if result else False
    else:
        newCard = Client_Cards(digits=newDigits, date_expires=newExpiration, CVV_code=newCVV_code, FK_idClient=client.id, type_card=attributedType)
        session.add(newCard)
        session.commit()

    return True if (newCard or result) else False

def register_new_client_pix_key(session: Session, key: str, CNPJ: str = None, CPF: str = None, type_pix: str = "random") -> bool:
    #TODO: make type_pix not mandatorial, return all registered pix
    
    if CNPJ:
       client: Clients = load_client_by_CNPJ(CNPJ, session)
    elif CPF: 
       client: Clients = load_client_by_CPF(CPF, session)
    else: raise Exception("Pix Key registration needs CNPJ or CPF to work.")

    if not client: raise HTTPException(detail="No client was found for the sent document.", status_code=404)

    try:
        attributedType = TypePixKey.from_str(type_pix)
    except ValueError:
        raise HTTPException(detail="No type of key is associated to the sent pix type.", status_code=404)
    

    #verify no key with same type exists for the client (1 type of each per client)
    stmt = select(Client_Pix_keys) \
            .join(Clients, Clients.id == Client_Pix_keys.FK_idClient) \
            .where(Clients.id == client.id) \
            .where(Client_Pix_keys.type_key == attributedType)
    keyTypeExists = session.exec(stmt).one_or_none()
    
    if keyTypeExists:
        raise HTTPException(detail=f"Pix with the type of key \'{attributedType.title()}\' already exists in database for this client.", status_code=409)

    #generate random key
    if attributedType == TypePixKey.RANDOM:
        key = generate_random_pix_key()

    newKey = Client_Pix_keys(type_key=attributedType, key=key, FK_idClient=client.id)
    session.add(newKey)
    session.commit()

    return True if newKey else False

# Getters
def load_client_by_CNPJ(CNPJ: str, session: Session) -> Clients:
    stmt = select(Clients).where(Clients.CNPJ == CNPJ)
    return session.exec(stmt).one_or_none()

def load_client_by_CPF(CPF: str, session: Session) -> Clients:
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
            "client_name": client.name,
            "client_address": result
        }

def load_client_cards(session: Session, CNPJ: str = None, CPF: str = None, type_card: str = None) -> dict[str, int | Client_Cards]:
    if CNPJ:
       client: Clients = load_client_by_CNPJ(CNPJ, session)
    elif CPF: 
       client: Clients = load_client_by_CPF(CPF, session)
    else: raise Exception("Address search needs CNPJ or CPF to work.")

    if not client: raise HTTPException(detail="No client was found when searching address.", status_code=404)


    stmt = select(Client_Cards) \
            .join(Clients, Clients.id == Client_Cards.FK_idClient) \
            .where(Clients.id == client.id) \
    
    if type_card:
        try:
            attributedType = TypeCard.from_str(type_card)
        except ValueError:
            raise HTTPException(detail="No type of key is associated to the sent pix type.", status_code=404)
        stmt = stmt.where(Client_Cards.type_card == attributedType)

    resultAll = session.exec(stmt).all()
    if not resultAll: raise HTTPException(detail="No card was found for the client and card type.", status_code=404)

    #interpreting before deliver
    length_result = len(resultAll)

    if not isinstance(resultAll, Client_Cards) and len(resultAll) == 1:
        resultAll = resultAll[0]
    
    return {
            "client_id": client.id,
            "client_name": client.name,
            f"client_card{'s' if length_result > 1 else ''}": resultAll
        }

def load_client_pix_keys(session: Session, CNPJ: str = None, CPF: str = None, type_pix: str = None) -> dict[str, int | Client_Pix_keys]:
    #TODO: make type_pix not mandatorial, return all registered pix

    if CNPJ:
       client: Clients = load_client_by_CNPJ(CNPJ, session)
    elif CPF: 
       client: Clients = load_client_by_CPF(CPF, session)
    else: raise Exception("Address search needs CNPJ or CPF to work.")

    if not client: raise HTTPException(detail="No client was found when searching address.", status_code=404)

    stmt = select(Client_Pix_keys) \
            .join(Clients, Clients.id == Client_Pix_keys.FK_idClient) \
            .where(Clients.id == client.id)

    if type_pix:
        try:
            attributedType = TypePixKey.from_str(type_pix)
        except ValueError:
            raise HTTPException(detail="No type of key is associated to the sent pix type.", status_code=404)
        stmt = stmt.where(Client_Pix_keys.type_key == attributedType)

    resultAll = session.exec(stmt).all()
    if not resultAll: raise HTTPException(detail="No card was found for the client and card type.", status_code=404)

    #interpreting before deliver
    length_result = len(resultAll)

    if not isinstance(resultAll, Client_Pix_keys) and len(resultAll) == 1:
        resultAll = resultAll[0]
    
    return {
            "client_id": client.id,
            "client_name": client.name,
            f"client_pix_key{'s' if length_result > 1 else ''}": resultAll
        }


# Alters #TODO
def change_client_active_status(session: Session, newStatus: bool, CPF: str = None, CNPJ: str = None): ...
def change_client_address(session: Session, newAddress: str, CPF: str = None, CNPJ: str = None): ...
def deactivate_client_card(session: Session, newStatus: bool, CPF: str = None, CNPJ: str = None): ...
def delete_client_pix_key(session: Session, newStatus: bool, CPF: str = None, CNPJ: str = None): ...
