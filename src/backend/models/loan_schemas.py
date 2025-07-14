from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from datetime import datetime

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from backend.models.main_schemas import Clients, Emitters

#Loans
class Type_Loan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)

    offers: List['Loan_offers'] = Relationship(back_populates="type_loan")

class Loan_offers(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str
    interest_rate: Decimal = Field(default=0.00, nullable=False)
    max_installment: int = Field(default=24, nullable=False)
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    active: bool = Field(default=True)
    date_deactivated: Optional[datetime]

    FK_idTypeLoan: Optional[int] = Field(foreign_key="type_loan.id")
    FK_idEmitter: int = Field(foreign_key="emitters.id")

    type_loan: Optional['Type_Loan'] = Relationship(back_populates="offers")
    emitter: 'Emitters' = Relationship(back_populates="loan_offers")
    loan_contracts: List['Loan_contracts'] = Relationship(back_populates="Loan_offer")

class Loan_contracts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    value: Decimal
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    installment_quantity: int = Field(default=1, nullable=False, ge=1)
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    paid: bool = Field(default=False)
    date_paid: Optional[datetime]
    active: bool = Field(default=False)
    date_deactivated = Field(default_factory=datetime.now, nullable=False)

    FK_idClient: int = Field(foreign_key="clients.id")
    FK_idLoanOffer: int = Field(foreign_key="loan_offers.id")

    client: 'Clients' = Relationship(back_populates="loan_contracts")
    loan_offer: 'Loan_offers' = Relationship(back_populates="loan_contracts")
    invoices: List['Loan_invoices'] = Relationship(back_populates="loan_contract")

class Loan_invoices(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    installment_number: int = Field(ge=1)
    value: Decimal
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    date_due: datetime = Field(nullable=False)
    paid: bool = Field(default=True)
    date_paid: Optional[datetime]

    FK_idLoanContract: int = Field(foreign_key="loan_contracts.id")

    loan_contract: 'Loan_contracts' = Relationship(back_populates="invoices")
