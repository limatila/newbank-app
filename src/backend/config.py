from dotenv import dotenv_values

#Instructions: for paths, please run from root

#.env locations
envFileName = ".env"
envFileName_alternatives = [

]

#pgsql
env = dotenv_values(envFileName)
PGSQL_CONNECTION_STRING = f"postgresql+psycopg2://{env.get('PG_USER', "root")}:{env.get('PG_PASSWORD', "1234")}@{env.get('PG_ADDRESS', "localhost")}:{env.get('PG_PORT', "5432")}/{env.get('PG_DBNAME', "newbank")}"