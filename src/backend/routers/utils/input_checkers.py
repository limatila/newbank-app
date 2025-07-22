from pydoc import doc
import re

#only numbers.
CNPJ_OFICIAL_LENGTH = 14
CPF_OFICIAL_LENGTH = 11

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
                assert len(result) == CNPJ_OFICIAL_LENGTH
            case 'CPF':
                assert len(result) == CPF_OFICIAL_LENGTH
            case _:
                raise AssertionError()
    except AssertionError:
        raise Exception("Error in document transformation, string could not be correctly transformed")

    return result
