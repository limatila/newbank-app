
#only numbers.
CNPJ_OFICIAL_LENGTH = 11
CPF_OFICIAL_LENGTH = 14

def check_CNPJ_length(CNPJ: str) -> bool:
    """
    Returns:
        bool: True if correct length (according to it's constant)
    """
    return len(CNPJ) == CNPJ_OFICIAL_LENGTH

def check_CPF_length(CPF: str) -> bool:
    """
    Returns:
        bool: True if correct length (according to it's constant)
    """
    return len(CPF) == CPF_OFICIAL_LENGTH