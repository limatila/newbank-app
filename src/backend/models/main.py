from typing import List, Optional
from sqlmodel import create_engine, SQLModel
from sqlmodel import Field, Relationship
from sqlmodel import UniqueConstraint

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, ge=1, le=MAX_POKEMON_NATIONAL_ID)
    name: str
    weight: Optional[float]   #Kg
    height: Optional[float]   #Meter
    description: Optional[str]

    #Relationships
    abilities: List['AbilityCompatibility'] = Relationship(back_populates="pokemons") #? needs to be mirrored with the anottated class

    #other constraints
    __table_args__ = (UniqueConstraint("name"), )
