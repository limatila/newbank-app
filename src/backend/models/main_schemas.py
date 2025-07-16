from typing import List, Optional, TYPE_CHECKING
from decimal import Decimal
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
from sqlmodel import UniqueConstraint

#oficial SQLModel's turn around to avoid circular imports
if TYPE_CHECKING:
    from backend.models.investment_schemas import Investment_contracts, Investment_offers
    from backend.models.loan_schemas import Loan_contracts, Loan_offers
    from backend.models.purchase_schemas import Credit_contracts, Credit_invoices, Credit_billings, Debit_historic, Payment_methods
    from backend.models.utils.enums import TypeCard, TypePixKey

SQLModel.metadata.clear() #clear first

#* Main entitys and stakeholder info
class Clients(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1, le=1000)
    name: str
    CPF: Optional[str] #talvez 2 tabelas para PF e PJ?
    CNPJ: Optional[str]
    debit_balance: Decimal = Field(default=0, ge=0)
    credit_balance: Decimal = Field(default=0)
    score: int = Field(default=500, ge=1, le=1000)
    card_default_date_closure: Optional[datetime]
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    active: bool = Field(default=True)
    date_deactivated: Optional[datetime]
    
    FK_idAddress: Optional[int] = Field(foreign_key="client_addresses.id")

    #Relationships
    address: Optional['Client_Addresses'] = Relationship(back_populates="client")
    cards: List['Cards'] = Relationship(back_populates="client")
    pix_keys: List['Pix_keys'] = Relationship(back_populates="client")
    debit_purchases: List['Debit_historic'] = Relationship(back_populates="client")
    credit_contracts: List['Credit_contracts'] = Relationship(back_populates="client")
    credit_billings: List['Credit_billings'] = Relationship(back_populates="client")
    credit_invoices: List['Credit_invoices'] = Relationship(back_populates="client")
    loan_contracts: List['Loan_contracts'] = Relationship(back_populates="client")
    investment_contracts: List['Investment_contracts'] = Relationship(back_populates="client")

    #other constraints
    __table_args__ = (UniqueConstraint("CPF"), UniqueConstraint("CNPJ"), )

class Client_Addresses(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    address: str
    number: str
    district: str
    complement: Optional[str]
    zip_code: Optional[str]
    CEP: Optional[str]
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)

    client: 'Clients' = Relationship(back_populates="address")

class Emitters(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str
    CNPJ: str
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    active: bool = Field(default=True)
    date_deactivated: Optional[datetime]

    credit_contracts: List['Credit_contracts'] = Relationship(back_populates="emitter")
    loan_offers: List['Loan_offers'] = Relationship(back_populates="emitter")
    investment_offers: List['Investment_offers'] = Relationship(back_populates="emitter")

    __table_args__ = (UniqueConstraint("CNPJ"), )

class Cards(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    digits: str
    date_expires: datetime
    CVV_code: str
    type_card: TypeCard = Field(default=TypeCard.PHYISICAL, nullable=False)
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    ativo: bool = Field(default=True)
    date_deactivated: Optional[datetime]

    FK_idCliente: int = Field(foreign_key="clients.id")

    client: Clients = Relationship(back_populates="cards")
    payment_methods: List['Payment_methods'] = Relationship(back_populates="card")

class Pix_keys(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    type_key: TypePixKey
    key: str
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)

    FK_idCliente: int = Field(foreign_key="clients.id")

    client: Clients = Relationship(back_populates="pix_keys")
    payment_methods: List['Payment_methods'] = Relationship(back_populates="pix_key")
