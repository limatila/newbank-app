from typing import List, Optional
from decimal import Decimal
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship
from sqlmodel import UniqueConstraint

from backend.config import PGSQL_CONNECTION_STRING

#* Main entitys and stakeholder info
class Clients(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1, le=1000)
    name: str
    CPF: Optional[str] #talvez 2 tabelas para PF e PJ?
    CNPJ: Optional[str]
    debit_balance: Decimal = Field(default=0, ge=0)
    crebit_balance: Decimal = Field(default=0, ge=0)
    
    FK_idAddress: Optional[int] = Field(foreign_key="client_addresses.id")

    # #Relationships
    # abilities: List['AbilityCompatibility'] = Relationship(back_populates="pokemons") #? needs to be mirrored with the anottated class

    #other constraints
    __table_args__ = (UniqueConstraint("CPF"), UniqueConstraint("CNPJ"))

class Client_Addresses(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    address: str
    number: str
    complement: str
    district: Optional[str]
    zip_code: Optional[str]
    CEP: Optional[str]

class Emitters(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str
    CNPJ: str

    __table_args__ = (UniqueConstraint("CNPJ"), )


#* Services and more
#Debit and Credit
class Type_Payment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str

class Debit_historic(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    CPF_receiver: Optional[str]
    CNPJ_receiver: Optional[str]
    value: Decimal

    FK_idTypePayment: Optional[int] = Field(foreign_key="type_payment.id")

    __table_args__ = (UniqueConstraint("CPF_receiver"), UniqueConstraint("CNPJ_receiver"))

class Credit_contracts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    CPF_receiver: Optional[str]
    CNPJ_receiver: Optional[str]
    value: Decimal

    FK_idTypePayment: Optional[int] = Field(foreign_key="type_payment.id")
    FK_idClient: Optional[int] = Field(foreign_key="clients.id")
    FK_idClient: Optional[int] = Field(foreign_key="emitters.id")

    __table_args__ = (UniqueConstraint("CPF_receiver"), UniqueConstraint("CNPJ_receiver"))

class Credit_invoices(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    value: Decimal
    closing_date: datetime

    FK_idCliente: Optional[int] = Field(foreign_key="clients.id")


#Investments and Loans
class Type_Loan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str

class Loan_options(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str
    interest_rate: Decimal = Field(default=0.00, nullable=False)
    max_installment: int = Field(default=24, nullable=False)

    FK_idEmitter: Optional[int] = Field(foreign_key="emitters.id")
    FK_idTypeLoan: Optional[int] = Field(foreign_key="type_loan.id")

class Loan_contract(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    value: Decimal
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    installment_quantity: int = Field(default=1, nullable=False)

class Type_Investment(SQLModel, table=True): #! shall be more studied because of additions and fees
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str #CDBs, CDIs, LCA, 'Tesouro Direto'
    profit_index: str #fixed, floating, hybrid

class Investment_options(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str
    interest_rate: Decimal = Field(default=0.00, nullable=False)
    min_funding: int = Field(default=0, nullable=False)
    max_funding: int = Field(default=10000, nullable=False)
    expiration_months: int #only for month count!

    FK_idEmitter: Optional[int] = Field(foreign_key="emitters.id")
    FK_idTypeInvestment: Optional[int] = Field(foreign_key="type_investment.id")

class Investment_contracts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    brute_applied_value: Decimal
    application_date: datetime = Field(default_factory=datetime.now, nullable=False)
    active: bool = Field(default=True)
    expiration_date = datetime

    FK_idInvestmentOption: Optional[int] = Field(foreign_key="investment_options.id")
    FK_idClient: Optional[int] = Field(foreign_key="clients.id")

#! First generation only
if __name__ == "__main__":
    from sqlmodel import create_engine

    engine = create_engine(PGSQL_CONNECTION_STRING,
                  echo=True, pool_pre_ping=True)
    SQLModel.metadata.create_all(engine)