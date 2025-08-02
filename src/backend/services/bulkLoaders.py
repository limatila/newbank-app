from typing import Any
import inspect

from fastapi import HTTPException
from sqlalchemy import Select, cast, collate
from sqlalchemy.types import String, VARCHAR
from sqlmodel import Sequence, Session, select, SQLModel, desc

from backend import models
from backend.config import DEBUG_MODE

#load all models into a dict
MODEL_CHOICES: dict[str, SQLModel] = { 
    name.lower(): obj 
    for name, obj in inspect.getmembers(models)
    if issubclass(obj, SQLModel) and not (obj is SQLModel)
}

def load_range_data(session: Session, choice: str, limit: int = 15, offset: int = 0, _return_stmt = False) -> Sequence[SQLModel] | Select:
    """loads a Sequence of any table at choice, or return a Select stmt to be processed in another function

    Args:
        model (SQLModel): the model to be loaded. Use one from backend.models to be searched here.
        limit (int, optional): limit size of Sequence, cannot be less then 0. Defaults to 15. If 0, will ignore limit
        offset (int, optional): positive offset of result, cannot be less then 0. Defaults to 0.

    Returns:
        Select | Sequence[SQLModel]: Returns the stmt or the loaded SQLModel
    """

    #get needed model
    model: SQLModel = MODEL_CHOICES.get(str(choice).lower(), None)
    if not model: raise HTTPException(detail="Your data_choice path is not referring to a existant model / table / data type.", status_code=403)

    stmt = select(model).order_by(model.id)

    if limit < 0: raise Exception("Limit cannot be 0 or negative.")
    if limit != 0: stmt = stmt.limit(limit)

    if offset:
        if offset < 0: raise Exception("Offset cannot be negative.")
        stmt = stmt.offset(offset)

    if _return_stmt:
        return stmt

    result = session.exec(stmt).all()

    if not result: raise HTTPException(detail="No Client was found for this criteria.", status_code=404)

    return result

def load_filtered_data(session: Session, stmt: Select, filterOption: str, filterValue: Any, _return_stmt = False) -> Sequence[SQLModel] | Select:
    """Add filter to Select stmt

    Returns:
        Sequence[SQLModel] | Select: Result, or Stmt for selection enrichment
    """

    #Get the model class from the raw column
    modelUsed = stmt.column_descriptions[0].get("entity", None)

    if modelUsed is None:
        raise ValueError("Could not determine model from the provided statement.")

    attribute = getattr(modelUsed, filterOption, None)

    if not attribute:
        raise HTTPException(detail=f"The filter_option '{filterOption}' is not an attribute of model '{modelUsed.__name__}'", status_code=403)
    
    column_type = attribute.property.columns[0].type #if varchar or int or etc.
    if DEBUG_MODE:
        print(f"Filtering column of type {column_type}")
    if isinstance(filterValue, str):
        stmt = stmt.where(attribute.ilike(filterValue))
    else:
        stmt = stmt.where(attribute == filterValue)

    if _return_stmt:
        return stmt

    result = session.exec(stmt).all()

    if not result:
        raise HTTPException(detail="No data was found for this criteria.", status_code=404)
    
    return result

def load_ordered_data(session: Session, stmt: Select, orderOption: str, orderOrientation: str = "ASC", _use_br_locale: bool = True) -> Sequence[SQLModel]: #final, no Select stmt return.
    """Add order to Select stmt

    Returns:
        Sequence[SQLModel] | Select: Result, or Stmt for selection enrichment
    """

    #Get the model class from the raw column
    modelUsed = stmt.column_descriptions[0].get("entity", None)

    if modelUsed is None:
        raise ValueError("Could not determine model from the provided statement.")

    attribute = getattr(modelUsed, orderOption, None)

    if not attribute:
        raise HTTPException(f"The order_option used does not correspond to an attribute from {modelUsed.__name__}", status_code=403)

    #order by
    column_type = attribute.property.columns[0].type #if varchar or int or etc.
    if DEBUG_MODE:
        print(f"Ordering column of type {column_type}")

    if isinstance(column_type, (String, VARCHAR)) and _use_br_locale:
        col_expr = collate(cast(attribute, String), 'pt-BR-x-icu')
    else:
        col_expr = attribute

    #empty previous order_by
    stmt = stmt.order_by(None)

    match(orderOrientation.upper()):
        case "ASC":
            stmt = stmt.order_by(col_expr)
        case "DESC":
            stmt = stmt.order_by(desc(col_expr))
        case _: raise HTTPException("The order_orientation inserted is not valid. Please choose between 'ASC' and 'DESC' for orientation", status_code=403)
    
    result: Sequence[SQLModel] = session.exec(stmt).all()

    if not result: raise HTTPException(detail="No data was found for this criteria.", status_code=404)


    return result
