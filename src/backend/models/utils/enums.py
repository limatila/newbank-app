from enum import Enum

class stringableEnum(str, Enum):
    @classmethod
    def from_str(cls, value: str):
        return cls(value.lower())

class ProfitIndex(stringableEnum):
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
    

if __name__ == "__main__":
    i = ProfitIndex.from_str("floating")
    print(i)
    print( ProfitIndex.from_str('fIxED') )
    print(ProfitIndex.HYBRID.title())

    j = TypePayment.from_str("pIx")
    print(j.title())
