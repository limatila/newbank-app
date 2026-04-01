from datetime import date

from fastapi import HTTPException, BackgroundTasks
from sqlmodel import Session, select

from backend.models import (
    Clients,
    Payment_methods,
    Debit_historic,
    Client_Cards,
    Client_Pix_keys,
)
from backend.models.utils.enums import (
    TypeMethodPayment,
    TypePayment,
    TypePixKey,
)
from backend.services.infomgmt.clientsmgmt import (
   load_client_by_CNPJ,
   load_client_by_CPF,
)

#? Utils
def verifyMethodExists(method: Payment_methods, session: Session) -> bool:
    #avoid duplicates
    methodExistsStmt = select(Payment_methods.id) \
                            .where(Payment_methods.method == method.method) \
                            .where(Payment_methods.FK_idCard == method.FK_idCard) \
                            .where(Payment_methods.FK_idPix == method.FK_idPix)
    return True if session.exec(methodExistsStmt).one_or_none() else False

# Create
def register_new_debit_payment(session: Session, payment_value: int, payment_method: str, payment_type: str, CNPJ: str = None, CPF: str = None, 
                                    card_digits: str = None, card_expiration_date: date = None, card_CVV: str = None, ) -> bool:
    #1: load payer
    if CNPJ:
       client: Clients = load_client_by_CNPJ(CNPJ, session)
    elif CPF: 
       client: Clients = load_client_by_CPF(CPF, session)
    else: raise Exception("Debit purchase needs CNPJ or CPF of a client.")

    #! verify null pointer client

    #2: get type method payment - how client pays
    method = TypeMethodPayment.from_str(payment_method) #! verify null pointer

    if not method.value.lower() in ["debit", "card", "virtual"]:
        raise HTTPException(detail="Informed payment_method is not valid! Please choose between: debit / card / virtual (card)", status_code=403)
    
    #get debit card 
    today = date.today()
    if card_expiration_date < today:
        raise HTTPException(detail="Informed card expiration date is invalid, it can't be already expired.", status_code=403)

    cardStmt = select(Client_Cards) \
                    .where(Client_Cards.digits == card_digits) \
                    .where(Client_Cards.CVV_code == card_CVV) \
                    .where(Client_Cards.date_expires == card_expiration_date)
    clientCard = session.exec(cardStmt).one_or_none() #! verify null pointer

    if clientCard.date_expires < today: Exception("Selected card was already expired, needs checkage!") 

    #3: get type of payment - how it's received (description)
    payment_type = TypePayment.from_str(payment_type) #! verify null pointer

    #4: register method payment 
    newMethod = Payment_methods(method=method, FK_idCard=clientCard)
    if not verifyMethodExists(newMethod, session):
        session.add(newMethod)
        session.commit()

    #? 5: get CPF/CNPJ of receiver (how to?)

    #6: register debit historic
    newRegistry = Debit_historic(type_payment=payment_type, value=payment_value, FK_idClient=client.id, FK_idMethodPayment=newMethod.id,
                                    CNPJ_receiver=None, CPF_receiver=None) #! attend to stage 5

    #7: subtract debit from client
    client.debit_balance -= payment_value
    session.add(client)
    session.commit()

    return True if (newRegistry and newMethod) else False

#TODO: make credit contract
#TODO: make pix payment