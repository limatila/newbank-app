from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint

from backend.models.utils.enums import TypePayment, TypeMethodPayment
if TYPE_CHECKING:
    from backend.models.main_schemas import Clients, Emitters, Pix_keys, Cards

#* Debit and Credit payments

class Payment_methods(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    type_payment: TypeMethodPayment = Field(default=TypeMethodPayment.DEBIT, nullable=False)
    
    FK_idPix: Optional[int] = Field(foreign_key="pix_keys.id")
    FK_idCard: Optional[int] = Field(foreign_key="cards.id")

    #pix, card
    pix_key: Optional['Pix_keys'] = Relationship(back_populates="payment_methods")
    card: Optional['Cards'] = Relationship(back_populates="payment_methods")
    debit_purchases: List['Debit_historic'] = Relationship(back_populates="client")
    credit_contracts: List['Credit_contracts'] = Relationship(back_populates="credit_contracts")

class Debit_historic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    type_payment: TypePayment = Field(default=TypeMethodPayment.DEBIT)
    CPF_receiver: Optional[str]
    CNPJ_receiver: Optional[str]
    value: Decimal
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)

    FK_idClient: int = Field(foreign_key="clients.id")
    FK_idMethodPayment: int = Field(foreign_key="payment_methods.id")

    client: 'Clients' = Relationship(back_populates="debit_registrys")
    method_payment: 'Payment_methods' = Relationship(back_populates="credit_contracts")

class Credit_contracts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    type_payment: TypePayment = Field(default=TypeMethodPayment.CARD)
    CPF_receiver: Optional[str]
    CNPJ_receiver: Optional[str]
    value: Decimal
    fiscal_note_number: str
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    paid: bool = Field(default=False)
    date_paid: Optional[datetime]

    FK_idClient: int = Field(foreign_key="clients.id")
    FK_idEmitter: int = Field(foreign_key="emitters.id")
    FK_idMethodPayment: int = Field(foreign_key="payment_methods.id")

    client: 'Clients' = Relationship(back_populates="credit_contracts")
    emitter: 'Emitters' = Relationship(back_populates="credit_contracts")
    method_payment: 'Payment_methods' = Relationship(back_populates="credit_contracts")
    credit_billings: List['Credit_billings'] = Relationship(back_populates="credit_contract")

    __table_args__ = (UniqueConstraint("CPF_receiver"), UniqueConstraint("CNPJ_receiver"))

class Credit_billings(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    value: Decimal
    installment_number: int = Field(ge=1)
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    paid: bool = Field(default=False)
    date_paid: Optional[datetime]

    FK_idCliente: int = Field(foreign_key="clients.id")
    FK_idCreditContract: int = Field(foreign_key="credit_contracts.id")

    client: 'Clients' = Relationship(back_populates="credit_billings")
    credit_contract: 'Credit_contracts' = Relationship(back_populates="credit_billings")

class Credit_invoices(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    total_value: Decimal = Field(default=0.00)
    bar_code: str
    pix_code: str
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    date_reference: datetime
    date_closure: datetime
    date_due: datetime
    paid: bool
    date_paid: Optional[datetime]

    FK_idClient: int = Field(foreign_key="clients.id")

    client: 'Clients' = Relationship(back_populates="credit_invoices")
