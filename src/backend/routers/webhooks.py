from os import system as CMD

from fastapi import APIRouter, Request

from backend.services.webhooks import update_local_code

webhooks_router = APIRouter(tags=["Webhooks"], prefix="/hooks")

@webhooks_router.post("/git-push", include_in_schema=False,
                       summary="A webhook accessed by github on a case of a Git Push. It'll update the code based on the main git branch")
def git_push_webhook(request: Request):
    return update_local_code()