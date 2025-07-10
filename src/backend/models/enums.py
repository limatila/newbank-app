from enum import Enum

class ProfitIndex(str, Enum):
    FIXED = "fixed"
    FLOATING = "floating"
    HYBRID = "hybrid"

    @classmethod
    def from_str(cls, value: str):
        return cls(value.lower())

if __name__ == "__main__":
    i = ProfitIndex.from_str("floating")
    print(i)
    print( ProfitIndex.from_str('fIxED') )
    print(ProfitIndex.HYBRID.title())