from os import system as CMD

from fastapi import APIRouter, Request

webhooks_router = APIRouter(tags=["DevOps"], prefix="hooks")

@webhooks_router.get("/git-push")
def git_push_gateway(request: Request):
    results: list[int] = []
    results.append( CMD("git -C ./api-pushed-code pull") )
    results.append( CMD("docker compose up --build") )
    results.append( CMD("docker compose restart api-pushed") )
    
    for r in results:
        if r != 0:
            error_index = results.index(r)
            return {"result": f"error in the {error_index}nd command."}

    return {"result": "success."}