#add all new schemas as star import, and models at __all__ registry
from .main_schemas import *
from .auth_schemas import *
from .purchase_schemas import *
from .loan_schemas import *
from .investment_schemas import *

__all__: list[str] = [
    "Clients",
    "Client_Addresses",
    "Client_Cards",
    "Client_Pix_keys",
    "Emitters",
    "Payment_methods",
    "Debit_historic",
    "Credit_contracts",
    "Credit_billings",
    "Credit_invoices",
    "Type_Loan", #! maybe will change to enum
    "Loan_offers",
    "Loan_contracts",
    "Loan_invoices",
    "Type_Investment",
    "Investment_contracts",
    "Investment_offers",
]