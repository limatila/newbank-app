from backend.models import *
from backend.dependencies.connections import get_engine
from sqlmodel import SQLModel

#! First generation only
#! subsequently, use updateDB.py
if __name__ == "__main__":
    from backend.dependencies.connections import get_engine

    engine = get_engine()
    SQLModel.metadata.create_all(engine)