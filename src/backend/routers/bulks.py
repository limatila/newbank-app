from typing import Any
from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends, HTTPException
from sqlmodel import Session

from backend.dependencies.connections import get_db_session
from backend.services.bulkLoaders import (
    load_filtered_data,
    load_ordered_data,
    load_range_data
)
from backend.routers.utils.input_checkers import (
    transform_document_to_digits,
    CNPJ_OFICIAL_LENGTH,
    CPF_OFICIAL_LENGTH,
)

bulk_router = APIRouter(prefix='/bulk', tags=['Bulk management'])

@bulk_router.get("/load/{data_choice}")
def load_multiple_data(data_choice: str, filter_option: str = None, filter_value: Any = None,
                            order_option: str = None, order_orientation: str = "ASC",
                            limit: int = 15, offset: int = 0, session: Session = Depends(get_db_session)):
    #validating load_range entrys
    if limit < 0: raise HTTPException("Limit cannot be 0 or negative.", status_code=403)
    if offset < 0: raise HTTPException("Offset cannot be negative.", status_code=403)

    result = load_range_data(session, data_choice, limit, offset, 
                                _return_stmt=(True if (filter_option or order_option) else False))

    #filtering
    if filter_option and filter_value:
        #validating filtering
        filter_option = filter_option.strip().lower()
        filter_value = filter_value.strip().lower()

        if filter_option.upper() in ["CNPJ", "CPF"]:
            filter_option = filter_option.upper()
            filter_value = filter_value.upper()

        try:
            match(filter_option):
                case "CNPJ":
                    filter_value = transform_document_to_digits(filter_value, "CNPJ")
                case "CPF":
                    filter_value = transform_document_to_digits(filter_value, "CPF")
                case _:
                    try:
                        filter_value = int(filter_value)
                    except ValueError:
                        pass
        except AssertionError:
            raise HTTPException(detail=f"Inserted {filter_option} is not valid. Please certify that the sent document has {CNPJ_OFICIAL_LENGTH if filter_option == "cnpj" else CPF_OFICIAL_LENGTH}", status_code=403) 

        if 'date' in filter_option:
            try:
                filter_value = datetime.strptime(filter_value, "%d-%m-%Y").date()
            except ValueError:
                HTTPException(detail="Inserted date for filter_value is on wrong format. Please use day-month-year ISO format.", status_code=403)

        result = load_filtered_data(session, result, filter_option, filter_value,
                                        _return_stmt=(True if order_option else False))
    elif not(filter_option and filter_value) and (filter_option or filter_value): 
        raise HTTPException(detail="for filtering, filter_option and filter_value are needed.", status_code=403)

    #ordering
    if order_option:
        #validating ordering
        order_option = order_option.strip().lower()
        order_orientation = order_orientation.strip().upper()
        result = load_ordered_data(session, result, order_option, order_orientation)

    #return all data
    return result