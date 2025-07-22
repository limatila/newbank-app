#main API executed in Backend
from fastapi import FastAPI

from backend.scripts.createDB import create_schema_in_first_startup
from backend.routers import redirections, webhooks
from backend.routers.inforouters import (
    clientsmgmt,
    emittersmgmt
)

#Instance
api = FastAPI(title="NewBank API", version="0.3", summary="API for interacting with NewBank's main database.")


#Routers
api.include_router(redirections.redirections_router)
api.include_router(webhooks.webhooks_router)
api.include_router(clientsmgmt.clients_router)
api.include_router(emittersmgmt.emitters_router)

@api.on_event("startup")
def startup_event():
    create_schema_in_first_startup()

@api.get("/healthcheck")
def health_check(name: str = None):
    return {
        "result": "healthy",
        "name": name
    }
