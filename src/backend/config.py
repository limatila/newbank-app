from dotenv import dotenv_values

#Instructions: for paths execution, please run from 'src/'
#.env locations
envFileName = ".env"
envFileName_alternatives = [
    "auth.env"
]

env = dotenv_values(envFileName)
# app variables
DEBUG_MODE = env.get('DEBUG', "True")

# for database connection
DB_ENGINE_CHOICE = env.get('DB_CHOICE', "sqlite")

#connection strings
SQLITE_CONNECTION_STRING = f"sqlite:///{env.get('SQLITE_FILE', "db.sqlite")}"
PGSQL_CONNECTION_STRING = f"postgresql+psycopg2://{env.get('PG_USER', "root")}:{env.get('PG_PASSWORD', "1234")}@{env.get('PG_HOST', "localhost")}:{env.get('PG_PORT', "5432")}/{env.get('PG_DBNAME', "newbank")}"

if DEBUG_MODE: print(env)