#main API executed in Backend

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from backend.routers import redirections, webhooks

#Instance
api = FastAPI(title="NewBank API", version="0.1", summary="API for interacting with NewBank's main database.")


#Routers
api.include_router(redirections.redirections_router)
api.include_router(webhooks.webhooks_router)