import re

from validate_docbr import CPF as CPFValidator, CNPJ as CNPJvalidator

#only numbers.
CNPJ_OFICIAL_LENGTH = 14
CPF_OFICIAL_LENGTH = 11

def check_CNPJ(CNPJ: str) -> bool:
    """
    Returns:
        bool: True if in terms with CNPJ legislation
    """
    validator = CNPJvalidator()
    return validator.validate(CNPJ)

def check_CPF(CPF: str) -> bool:
    """
    Returns:
        bool: True if in terms with CPF legislation
    """
    validator = CPFValidator()
    return validator.validate(CPF)

def transform_document_to_digits(entry: str, documentType: str) -> str:
    """
    Args:
        entry (str): string to be transformed
        documentType (str): "CPF" or "CNPJ", only.

    Returns:
        str: 11 or 14 digits for the 'documentType'
    """

    entry = entry.replace('%2F', '')  # In case double encoding slipped in
    result = re.sub(r"\D", "", entry)

    try:
        assert isinstance(result, str)
        assert result.isdigit()
        match(documentType):
            case 'CNPJ':
                assert check_CNPJ(entry) == True
            case 'CPF':
                assert check_CPF(entry) == True
            case _:
                raise AssertionError()
    except AssertionError:
        raise Exception("Error in document transformation, string could not be correctly transformed")

    return result
