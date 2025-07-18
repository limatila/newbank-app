import secrets
import re
import uuid
from datetime import date
from dateutil.relativedelta import relativedelta

from backend.config import CARD_PREFIX, RANDOM_KEY_POSFIX

CARD_DIGITS_LENGTH: int = 16
CARD_CVV_LENGTH: int = 3

def luhn_checksum(card_number: str) -> int:
    def digits_of(entry):
        entry = re.sub(r"\D", "", str(entry))
        assert len(entry) == CARD_DIGITS_LENGTH
        return [int(d) for d in entry]

    digits = digits_of(card_number)
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        doubled = d * 2
        checksum += doubled if doubled < 10 else doubled - 9
    return checksum % 10

def generate_new_card_digits(_bin_prefix: str = CARD_PREFIX) -> str:
    if len(_bin_prefix) >= CARD_DIGITS_LENGTH - 1:
        raise ValueError("BIN prefix too long for desired card number length.")

    number = _bin_prefix
    while len(number) < (CARD_DIGITS_LENGTH - 1):
        number += str(secrets.randbelow(10))  # Secure digit generation

    checksum = luhn_checksum(number + "0")
    check_digit = (10 - checksum) % 10
    return number + str(check_digit)

def generate_new_card_CVV_code() -> str:
    result = []

    for _ in range(CARD_CVV_LENGTH):
        result.append( str(secrets.randbelow(10)) )

    return "".join(result)

def generate_new_card_date_expiration() -> date:
    now: date = date.today()
    years_to_expire = 5
    return (now + relativedelta(years=years_to_expire)).replace(day=1)

def generate_new_credit_balance(CNPJ: str = None, CPF: str = None) -> float:
    if not CNPJ and not CPF: 
        raise Exception("Credit generation needs CNPJ or CPF to work.")   

    #? random algorithm. Should be a formula based in Serasa's score, but it's a paid service.
    new_credit = secrets.randbelow(len(CNPJ if CNPJ else CPF)) / 2.15
    return new_credit * 100

def generate_random_pix_key(_bin_posfix = RANDOM_KEY_POSFIX) -> str:
    return uuid.uuid4().__str__() + _bin_posfix

if __name__ == "__main__":
    print(generate_new_card_digits())
    print(generate_new_card_CVV_code())
    print(generate_new_card_date_expiration())
    print(generate_new_credit_balance(CNPJ="152313"))