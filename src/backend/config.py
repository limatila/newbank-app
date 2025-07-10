from dotenv import dotenv_values

#Instructions: for paths, please run from root

#.env locations
envFileName = ".env"
envFileName_alternatives = [
    "auth.env"
]

# for database connection
env = dotenv_values(envFileName)

DB_ENGINE_CHOICE = env.get('DB_CHOICE', "sqlite")

#connection strings
PGSQL_CONNECTION_STRING = f"postgresql+psycopg2://{env.get('PG_USER', "root")}:{env.get('PG_PASSWORD', "1234")}@{env.get('PG_ADDRESS', "localhost")}:{env.get('PG_PORT', "5432")}/{env.get('PG_DBNAME', "newbank")}"
SQLITE_CONNECTION_STRING = f"sqlite:///{env.get('SQLITE_FILE'), "db.sqlite"}"