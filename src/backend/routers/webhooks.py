from os import system as CMD

from fastapi import APIRouter, Request

webhooks_router = APIRouter(tags=["Webhooks"], prefix="/hooks")

@webhooks_router.get("/git-push", summary="A webhook accessed by github on a case of a Git Push. It'll update the code based on the main git branch")
def git_push_webhook(request: Request):
    results: list[int] = []
    results.append( CMD("git -C ./src pull") )
    results.append( CMD("docker compose up --build") )
    results.append( CMD("docker compose restart api-pushed") )
    
    for r in results:
        if r != 0:
            error_index = results.index(r)
            return {"result": f"error in the {error_index}nd command."}

    return {"result": "success."}