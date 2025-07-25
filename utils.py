import sys
from models.node import Node
from models.relationship import Relationship

def exit(exit_code, db_name, mongoClient, neoClient):
    print("\nExiting the system...")
    mongoClient.drop_database(db_name)
    with neoClient.session(database="system") as session:
        session.run(f"DROP DATABASE {db_name} IF EXISTS")

    mongoClient.close()
    neoClient.close()

    sys.exit(exit_code)
