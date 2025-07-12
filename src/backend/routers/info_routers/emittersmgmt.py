from fastapi import APIRouter
from fastapi import Depends, HTTPException

from backend.services.infomgmt.emittersmgmt import (
    register_new_emitter,
    load_emitter_by_CNPJ,
)

emitters_router = APIRouter(prefix='/emitters', tags=['Emitter info'])