#Automated migration -- execute for fast db upgrade experience
#* script imported from: https://github.com/limatila/programacao--study/blob/fastapi-pokedex/pokedex/models/makeMigration.py. Author: Átila Lima (me).

#PLEASE RUN THIS FILE AT ROOT DIR (/newbank-app/)
#Will execute despite the models have changed or not

#! Add new models to models/__init__.py (via import) 
from os import system as cmd
import datetime

from backend.scripts.createDB import messagesPrefix

migrationMessage = str(input(f"{messagesPrefix}Please enter a migration message\t->"))

result = cmd(f"alembic revision --autogenerate -m \"{migrationMessage}\"")

result_2: int = -10
if result == 0:
    choiceMigrateNow = str(input(f"{messagesPrefix}Migration created. Migrate Now? (y/N)\t->"))
    if choiceMigrateNow.lower().startswith("y"):
        result_2 = cmd("alembic upgrade head")

#Logging
if result == 0 and result_2 == 0:
    with open('migration-history.log', 'a') as file:
        now = datetime.datetime.now()
        file.write(f"\n[{now}] -- Migration sucessfull: {migrationMessage}")
elif result == 0 and result_2 == -10:
    with open('migration-history.log', 'a') as file:
        now = datetime.datetime.now()
        file.write(f"\n[{now}] -- Migration created (ready to migrate): {migrationMessage}")
        print(f"{messagesPrefix}Migration created. Migrate with: \'alembic upgrade head\'")
else: 
    print(f"{messagesPrefix}Migration was not created.")
