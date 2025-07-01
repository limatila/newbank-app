from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse 
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

redirections_router = APIRouter(include_in_schema=False)

@redirections_router.get('/', description="redirects Root url to Documentation page")
def root_redirect(request: Request):
    return RedirectResponse("/docs", headers={"result": "redirected to Documentation page (at \'/docs\')"})

@redirections_router.get("/docs")
def docs(request: Request):
    return get_swagger_ui_html(openapi_url="/openapi.json", title="YCC Docs")

@redirections_router.get("/openapi.json")
def openapi(request: Request):
    return JSONResponse(get_openapi(title=redirections_router.title, version=redirections_router.version, routes=redirections_router.routes))
