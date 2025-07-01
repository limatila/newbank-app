#main API executed in Backend

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from routers import redirections

app = FastAPI(title="NewBank API", summary="API for interacting with NewBank's main database.")

app.include_router(redirections.redirections_router)