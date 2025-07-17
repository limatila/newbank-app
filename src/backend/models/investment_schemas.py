from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from datetime import date, datetime

from sqlmodel import SQLModel, Field, Relationship

from backend.models.utils.enums import ProfitIndex
if TYPE_CHECKING:
    from backend.models.main_schemas import Clients, Emitters

#Investments
class Type_Investment(SQLModel, table=True): #! shall be more studied because of additions and fees
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str #CDBs, CDIs, LCA, 'Tesouro Direto'
    profit_index: Optional[ProfitIndex] = Field(default=ProfitIndex.FIXED, nullable=False)
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)

    offers: List['Investment_offers'] = Relationship(back_populates="type_investment")

class Investment_offers(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    name: str
    interest_rate: Decimal = Field(default=0.00, nullable=False)
    min_funding: Decimal = Field(default=0.00, nullable=False)
    max_funding: Decimal = Field(default=10000.00, nullable=False)
    expiration_months: int #only for month count!
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    active: bool = Field(default=True)
    date_deactivated: Optional[datetime]

    FK_idTypeInvestment: Optional[int] = Field(foreign_key="type_investment.id")
    FK_idEmitter: int = Field(foreign_key="emitters.id")

    type_investment: Optional['Type_Investment'] = Relationship(back_populates="offers")
    emitter: 'Emitters' = Relationship(back_populates="investment_offers")
    contracts: List['Investment_contracts'] = Relationship(back_populates="investment_offer")

class Investment_contracts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1)
    gross_applied_value: Decimal
    date_approved: datetime = Field(default_factory=datetime.now, nullable=False)
    date_expiration: date = Field(nullable=False)
    active: bool = Field(default=True)
    date_deactivated: Optional[datetime]

    FK_idInvestmentOffer: int = Field(foreign_key="investment_offers.id")
    FK_idClient: int = Field(foreign_key="clients.id")

    investment_offer: 'Investment_offers' = Relationship(back_populates="contracts")
    client: 'Clients' = Relationship(back_populates="investment_contracts")
