# First db creation script
#! You can run it manually, or it will be runned on API startup.

from sqlmodel import SQLModel
from sqlalchemy import inspect
from backend.dependencies.connections import get_engine
from backend.models import *
from backend.models.utils.enums import *

messagesPrefix = "[SCRIPT] "

def create_schema_in_first_startup():
    engine = get_engine(debug='False')
    inspector = inspect(engine)
    
    if not inspector.has_table("clients") or not inspector.has_table("debit_historic"): #core tables
        print(f"{messagesPrefix}Creating DB tables in first api startup **")
        SQLModel.metadata.create_all(engine)
        print(f"{messagesPrefix}DBs created!")

if __name__ == "__main__":
    create_schema_in_first_startup()