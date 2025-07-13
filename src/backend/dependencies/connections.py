from sqlmodel import create_engine, Session 

from backend.config import DEBUG_MODE, DB_ENGINE_CHOICE, PGSQL_CONNECTION_STRING, SQLITE_CONNECTION_STRING

#* Engines: for manual usage
def get_engine(engineChoice: str = DB_ENGINE_CHOICE, debug: str = DEBUG_MODE):
    """
    Returns a SQLModel Engine for SQLModel Sessions.
    
        engineChoice: select the DB to be used, mainly with config.DB_ENGINE_CHOICE. 
            - 'sqlite'
            - 'sqlite3'
            - 'pgsql'

        Raises Exception for invalid cases
    """
    match(engineChoice):
        case "sqlite" | "sqlite3":
            return create_engine(SQLITE_CONNECTION_STRING)
        case "pgsql":
            return create_engine(PGSQL_CONNECTION_STRING, pool_pre_ping=True, echo=True if (debug.title() == 'True') else False)
        case _:
            raise Exception("Not a valid choice of engine, \nplease select between \"sqlite\" and \"pgsql\".")

#* For FastAPI.Depends
def get_db_session_dependency():
    """
    Yields a created session for use in FastAPI decorated Functions with the 'Depends' function in params\n
    Expects that config.DB_ENGINE_CHOICE global variable is either:
        - 'sqlite'
        - 'sqlite3'
        - 'pgsql'

    Raises Exception for invalid cases
    """
    match(DB_ENGINE_CHOICE):
        case "sqlite" | "sqlite3":
            with Session(get_engine("sqlite3")) as session:
                yield session
        case "pgsql":
            with Session(get_engine("pgsql")) as session:
                yield session
        case _:
            raise Exception("Not a valid choice of engine for the generator, \nplease select between \"sqlite\" and \"pgsql\".")
    
if __name__ == "__main__":
    an_engine = get_engine(DB_ENGINE_CHOICE)