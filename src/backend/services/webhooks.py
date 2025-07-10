
from os import system as CMD

def update_local_code():
    results: list[int] = []
    results.append( CMD("git -C ../ pull") )
    
    for r in results:
        if r != 0:
            error_index = results.index(r)
            return {"result": f"error in the {1 + error_index}nd command."}

    return {"result": "success."}