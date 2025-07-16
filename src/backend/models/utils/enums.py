from enum import Enum

class stringableEnum(str, Enum):
    @classmethod
    def from_str(cls, value: str):
        return cls(value.lower())

class ProfitIndex(stringableEnum):
    """
    Demonstrating Types of Investments
    """
    FIXED = "fixed"
    FLOATING = "floating"
    HYBRID = "hybrid"

class TypePayment(stringableEnum):
    """
    Types of payments: Invoices, PIX, TED, Withdraw, Credit Invoice
    """
    INVOICE = "invoice"
    PIX = "pix"
    WITHDRAW = "withdraw"
    CREDIT_INVOICE = "credit"

class TypeMethodPayment(stringableEnum):
    """
    Types of Payment Methods (which client can use)
    """
    PIX = "pix"
    CARD = "card"
    VIRTUAL_CARD = "virtual"
    DEBIT = "debit"

class TypeCard(stringableEnum):
    PHYISICAL = "physical"
    VIRTUAL = "virtual"

class TypePixKey(stringableEnum):
    CPF = "cpf"
    CNPJ = "cnpj"
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"
    RANDOM = "random"

if __name__ == "__main__":
    i = ProfitIndex.from_str("floating")
    print(i)
    print( ProfitIndex.from_str('fIxED') )
    print(ProfitIndex.HYBRID.title())

    j = TypePayment.from_str("pIx")
    print(j.title())
