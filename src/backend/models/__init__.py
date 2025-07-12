#add all new schemas as star import, and models at __all__ registry
from .main_schemas import *
from .auth_schemas import *
from .purchase_schemas import *
from .loan_schemas import *
from .investment_schemas import *

__all__: list[str] = [
    "Clients",
    "Emitters",
    "Client_Addresses",
    "Type_Payment",
    "Type_Investment",
    "Type_Loan",
    "Debit_historic",
    "Credit_contracts",
    "Credit_invoices",
    "Investment_contracts",
    "Investment_offers",
    "Loan_contracts",
    "Loan_offers",
]