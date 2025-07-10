from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
from sqlmodel import UniqueConstraint

from backend.models.enums import ProfitIndex

SQLModel.metadata.clear() #clear first

#* Main entitys and stakeholder info
class Clients(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1, le=1000)
    name: str
    CPF: Optional[str] #talvez 2 tabelas para PF e PJ?
    CNPJ: Optional[str]
    debit_balance: Decimal = Field(default=0, ge=0)
    crebit_balance: Decimal = Field(default=0, ge=0)
    
    FK_idAddress: Optional[int] = Field(foreign_key="client_addresses.id")

    #Relationships
    address: Optional['Client_Addresses'] = Relationship(back_populates="client") #? needs to be mirrored with the anottated class
    debit_purchases: List['Debit_historic'] = Relationship(back_populates="client")
    credit_contracts: List['Credit_contracts'] = Relationship(back_populates="client")
    credit_invoices: List['Credit_invoices'] = Relationship(back_populates="client")
    loan_contracts: List['Loan_contracts'] = Relationship(back_populates="client")
    investment_contracts: List['Investment_contracts'] = Relationship(back_populates="client")

    #other constraints
    __table_args__ = (UniqueConstraint("CPF"), UniqueConstraint("CNPJ"), UniqueConstraint("FK_idAddress"))

class Client_Addresses(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    address: str
    number: str
    complement: str
    district: Optional[str]
    zip_code: Optional[str]
    CEP: Optional[str]

    client: 'Clients' = Relationship(back_populates="address")

class Emitters(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str
    CNPJ: str

    credit_contracts: List['Credit_contracts'] = Relationship(back_populates="emitter")
    loan_offers: List['Loan_offers'] = Relationship(back_populates="emitter")
    investment_offers: List['Investment_offers'] = Relationship(back_populates="emitter")

    __table_args__ = (UniqueConstraint("CNPJ"), )


#* Services and more
#Debit and Credit
class Type_Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str

    debits: List['Debit_historic'] = Relationship(back_populates="type_payment")
    credits: List['Credit_contracts'] = Relationship(back_populates="type_payment")

class Debit_historic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    CPF_receiver: Optional[str]
    CNPJ_receiver: Optional[str]
    value: Decimal

    FK_idTypePayment: Optional[int] = Field(foreign_key="type_payment.id")
    FK_idClient: int = Field(foreign_key="clients.id")

    type_payment: Optional['Type_Payment'] = Relationship(back_populates="debits")
    client: 'Clients' = Relationship(back_populates="debit_purchases")

class Credit_contracts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    CPF_receiver: Optional[str]
    CNPJ_receiver: Optional[str]
    value: Decimal

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
    due_date: datetime = Field(nullable=False)

    FK_idCliente: int = Field(foreign_key="clients.id")

    client: 'Clients' = Relationship(back_populates="credit_invoices")


#Loans and Investments
class Type_Loan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str

    offers: List['Loan_offers'] = Relationship(back_populates="type_loan")

class Loan_offers(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str
    interest_rate: Decimal = Field(default=0.00, nullable=False)
    max_installment: int = Field(default=24, nullable=False)

    FK_idTypeLoan: Optional[int] = Field(foreign_key="type_loan.id")
    FK_idEmitter: int = Field(foreign_key="emitters.id")

    type_loan: Optional['Type_Loan'] = Relationship(back_populates="offers")
    emitter: 'Emitters' = Relationship(back_populates="loan_offers")

class Loan_contracts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    value: Decimal
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    installment_quantity: int = Field(default=1, nullable=False)

    FK_idClient: int = Field(foreign_key="clients.id")

    client: 'Clients' = Relationship(back_populates="loan_contracts")
    invoices: List['Loan_invoices'] = Relationship(back_populates="loan_contract")

class Loan_invoices(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    installment_number: int = Field(ge=1)
    value: Decimal
    due_date: datetime = Field(nullable=False)

    FK_idLoanContract: int = Field(foreign_key="loan_contracts.id")

    loan_contract: 'Loan_contracts' = Relationship(back_populates="invoices")

class Type_Investment(SQLModel, table=True): #! shall be more studied because of additions and fees
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str #CDBs, CDIs, LCA, 'Tesouro Direto'
    profit_index: Optional[ProfitIndex] = Field(default=ProfitIndex.FIXED, nullable=False)

    offers: List['Investment_offers'] = Relationship(back_populates="type_investment")

class Investment_offers(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str
    interest_rate: Decimal = Field(default=0.00, nullable=False)
    min_funding: int = Field(default=0, nullable=False)
    max_funding: int = Field(default=10000, nullable=False)
    expiration_months: int #only for month count!

    FK_idTypeInvestment: Optional[int] = Field(foreign_key="type_investment.id")
    FK_idEmitter: int = Field(foreign_key="emitters.id")

    type_investment: Optional['Type_Investment'] = Relationship(back_populates="offers")
    emitter: 'Emitters' = Relationship(back_populates="investment_offers")
    contracts: List['Investment_contracts'] = Relationship(back_populates="investment_offer")

class Investment_contracts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    gross_applied_value: Decimal
    application_date: datetime = Field(default_factory=datetime.now, nullable=False)
    active: bool = Field(default=True)
    expiration_date: datetime = Field(nullable=False)

    FK_idInvestmentOffer: int = Field(foreign_key="investment_offers.id")
    FK_idClient: int = Field(foreign_key="clients.id")

    investment_offer: 'Investment_offers' = Relationship(back_populates="contracts")
    client: 'Clients' = Relationship(back_populates="investment_contracts")

#! First generation only
#! subsequently, use makeMigration.py
if __name__ == "__main__":
    from backend.dependencies.connections import get_engine

    engine = get_engine()
    SQLModel.metadata.create_all(engine)