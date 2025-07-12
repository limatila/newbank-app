from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship, UniqueConstraint

if TYPE_CHECKING:
    from backend.models.main_schemas import Clients, Emitters

#* Services and more
#Debit and Credit
class Type_Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)

    debits: List['Debit_historic'] = Relationship(back_populates="type_payment")
    credits: List['Credit_contracts'] = Relationship(back_populates="type_payment")

class Debit_historic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    CPF_receiver: Optional[str]
    CNPJ_receiver: Optional[str]
    value: Decimal
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)

    FK_idTypePayment: Optional[int] = Field(foreign_key="type_payment.id")
    FK_idClient: int = Field(foreign_key="clients.id")

    type_payment: Optional['Type_Payment'] = Relationship(back_populates="debits")
    client: 'Clients' = Relationship(back_populates="debit_purchases")

class Credit_contracts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    CPF_receiver: Optional[str]
    CNPJ_receiver: Optional[str]
    value: Decimal
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    paid: bool = Field(default=False)

    FK_idTypePayment: Optional[int] = Field(foreign_key="type_payment.id")
    FK_idClient: int = Field(foreign_key="clients.id")
    FK_idEmitter: int = Field(foreign_key="emitters.id")

    type_payment: Optional['Type_Payment'] = Relationship(back_populates="credits")
    client: 'Clients' = Relationship(back_populates="credit_contracts")
    emitter: 'Emitters' = Relationship(back_populates="credit_contracts")

    __table_args__ = (UniqueConstraint("CPF_receiver"), UniqueConstraint("CNPJ_receiver"))

class Credit_invoices(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    value: Decimal
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    date_due: datetime = Field(nullable=False)
    installment_number: int = Field(ge=1)

    FK_idCliente: int = Field(foreign_key="clients.id")

    client: 'Clients' = Relationship(back_populates="credit_invoices")