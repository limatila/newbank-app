from datetime import date, datetime

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
    else: raise Exception("Card registration needs CNPJ or CPF of a client.")

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
        if __recursion_flag < 10:
            result = register_new_client_card(session, CNPJ, CPF, type_card, 
                                              __recursion_flag=(__recursion_flag + 1)) #recursive, limited at ten tries
        return True if result else False
    else:
        newCard = Client_Cards(digits=newDigits, date_expires=newExpiration, CVV_code=newCVV_code, FK_idClient=client.id, type_card=attributedType)
        session.add(newCard)
        session.commit()

    return True if (newCard or result) else False

def register_new_client_pix_key(session: Session, key: str, CNPJ: str = None, CPF: str = None, type_pix: str = "random") -> bool:    
    if CNPJ:
       client: Clients = load_client_by_CNPJ(CNPJ, session)
    elif CPF: 
       client: Clients = load_client_by_CPF(CPF, session)
    else: raise Exception("Pix Key registration needs CNPJ or CPF of a client.")

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
def load_client_by_CNPJ(CNPJ: str, session: Session) -> Clients | None:
    stmt = select(Clients).where(Clients.CNPJ == CNPJ)
    result = session.exec(stmt).one_or_none()
    if not result: raise HTTPException(detail="No client was found for the sent document.", status_code=404)

    return result 

def load_client_by_CPF(CPF: str, session: Session) -> Clients | None:
    stmt = select(Clients).where(Clients.CPF == CPF)
    result = session.exec(stmt).one_or_none()
    if not result: raise HTTPException(detail="No client was found for the sent document.", status_code=404)

    return result 

def load_client_address(session: Session, CNPJ: str = None, CPF: str = None) -> dict[str, int | str | Client_Addresses]:
    try:
        if CNPJ:
            client: Clients = load_client_by_CNPJ(CNPJ, session)
        elif CPF: 
            client: Clients = load_client_by_CPF(CPF, session)
        else: raise Exception("Address search needs CNPJ or CPF of a client.")
    except HTTPException(status_code=404): 
        raise HTTPException(detail="No client was found when searching address.", status_code=404)

    stmt = select(Client_Addresses).join(Clients) \
                    .where(Clients.id == client.id).order_by(Client_Addresses.id)
    result = session.exec(stmt).one_or_none()
    if not result: raise HTTPException(detail="No address was found for this client.", status_code=404)

    #interpreting before deliver
    return {
            "client_id": client.id,
            "client_name": client.name,
            "client_address": result
        }

def load_client_cards(session: Session, CNPJ: str = None, CPF: str = None, type_card: str = None) -> dict[str, int | str | Client_Cards |  Sequence[Client_Cards]]:
    try:
        if CNPJ:
            client: Clients = load_client_by_CNPJ(CNPJ, session)
        elif CPF: 
            client: Clients = load_client_by_CPF(CPF, session)
        else: raise Exception("Card search needs CNPJ or CPF of a client.")
    except HTTPException:
        raise HTTPException(detail="No client was found when searching registered cards.", status_code=404)

    stmt = select(Client_Cards) \
            .join(Clients, Clients.id == Client_Cards.FK_idClient) \
            .where(Clients.id == client.id)
    
    if type_card:
        try:
            attributedType = TypeCard.from_str(type_card)
        except ValueError:
            raise HTTPException(detail="No type of key is associated to the sent pix type.", status_code=403)
        stmt = stmt.where(Client_Cards.type_card == attributedType)

    resultAll = session.exec(stmt).all()
    if not resultAll: raise HTTPException(detail="No card was found for the client and card type.", status_code=404)

    #interpreting before deliver
    if not isinstance(resultAll, Client_Cards) and len(resultAll) == 1:
        resultAll = resultAll[0]
    
    return {
            "client_id": client.id,
            "client_name": client.name,
            "client_cards": resultAll
        }

def load_client_pix_keys(session: Session, CNPJ: str = None, CPF: str = None, type_pix: str = None) -> dict[str, int | str | Client_Pix_keys | Sequence[Client_Pix_keys]]:
    try:
        if CNPJ:
            client: Clients = load_client_by_CNPJ(CNPJ, session)
        elif CPF: 
            client: Clients = load_client_by_CPF(CPF, session)
        else: raise Exception("Pix key search needs CNPJ or CPF of a client.")
    except HTTPException:
        raise HTTPException(detail="No client was found when searching registered pix keys.", status_code=404)

    stmt = select(Client_Pix_keys) \
            .join(Clients, Clients.id == Client_Pix_keys.FK_idClient) \
            .where(Clients.id == client.id)

    if type_pix:
        try:
            attributedType = TypePixKey.from_str(type_pix)
        except ValueError:
            raise HTTPException(detail="No type of key is associated to the sent pix type.", status_code=403)
        stmt = stmt.where(Client_Pix_keys.type_key == attributedType)

    resultAll = session.exec(stmt).all()
    if not resultAll: raise HTTPException(detail=f"No pix key was found for the client{" and pix type." if type_pix else '.'}", status_code=404)

    #interpreting before deliver
    if not isinstance(resultAll, Client_Pix_keys) and len(resultAll) == 1:
        resultAll = resultAll[0]
    
    return {
            "client_id": client.id,
            "client_name": client.name,
            f"client_pix_keys": resultAll
        }


# Alters
def change_client_active_status(session: Session, newStatus: bool, CNPJ: str = None, CPF: str = None, ) -> dict[str, str | datetime]: 
    if CNPJ:
       client: Clients = load_client_by_CNPJ(CNPJ, session)
    elif CPF: 
       client: Clients = load_client_by_CPF(CPF, session)
    else: raise Exception("Client status change needs CNPJ or CPF of a client.")

    wasDeactivated, wasEqualStatus = (False, False)

    #modeling response
    if newStatus == client.active:
        wasEqualStatus = True

    #alter it
    client.active = newStatus
    #adding deactivation date
    if newStatus == False:
        newDeactivationDate = datetime.now() 
        client.date_deactivated = newDeactivationDate
        wasDeactivated = True

    if not wasEqualStatus:
        session.add(client)
        session.commit()

    result = {
        "result": "success",
    }
    if wasEqualStatus: result.update({"detail": f"Client was already at state {'active' if newStatus else 'deactivated'}"})
    if wasDeactivated: result.update({"date_deactivated": client.date_deactivated})

    return result

def change_client_address(session: Session, address: str, address_number: str, complement: str, district: str, 
                            zip_code: str = None, CEP: str = None, CNPJ: str = None, CPF: str = None) -> bool:
    if CNPJ:
       client: Clients = load_client_by_CNPJ(CNPJ, session)
    elif CPF: 
       client: Clients = load_client_by_CPF(CPF, session)
    else: raise Exception("Address change needs CNPJ or CPF of a client.")

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

    #affiliating address to client
    client.FK_idAddress = newAddress.id
    session.add(client)
    session.commit()

    return True if client else False

def deactivate_client_card(session: Session, card_digits: str, card_expiration: date, card_CVV: str, CNPJ: str = None, CPF: str = None) -> dict[str, str | datetime]:
    if not CNPJ and not CPF: raise Exception("Client' card deactivation needs CNPJ or CPF of a client.")

    stmt = select(Client_Cards) \
            .where(Client_Cards.digits == card_digits) \
            .where(Client_Cards.date_expires == card_expiration) \
            .where(Client_Cards.CVV_code == card_CVV)
    client_card = session.exec(stmt).one_or_none()

    if not client_card: raise HTTPException(detail="No client card was found for this card data", status_code=404)

    wasDeactivatedStatus = False

    if False == client_card.active:
        #modeling response
        wasDeactivatedStatus = True
    else:
        #adding deactivation date
        newDeactivationDate = datetime.now() 
        client_card.date_deactivated = newDeactivationDate

        #alter it
        client_card.active = False
        session.add(client_card)
        session.commit()

    result = {
        "result": "success",
    }
    if wasDeactivatedStatus: result.update({"detail": f"Card was already at state deactivated"})
    result.update({"date_deactivated": client_card.date_deactivated})

    return result

def delete_client_pix_key(session: Session, type_pix: str, CNPJ: str = None, CPF: str = None) -> dict[str, str | TypePixKey]:
    if CNPJ or CPF:
       client_pix_key_results = load_client_pix_keys(session, CNPJ, CPF, type_pix)
    elif not CNPJ and not CPF: raise Exception("Client pix key deletion operation needs CNPJ or CPF of a client.")

    #extract pix from result
    pix_key: Client_Pix_keys = client_pix_key_results.get("client_pix_keys", None)

    if not pix_key: 
        raise HTTPException(detail="No pix key was found for the sent document and pix type.", status_code=404)

    session.delete(pix_key)
    session.commit()

    return {
        "result": "success",
        "type_deleted": pix_key.type_key,
        "key_deleted": pix_key.key
    }

#TODO: add routes, test, review arg positions