from gui import GUI
from mongodb import connect_mongo, create_db, load_documents, queryOne
from utils import exit
from neo import connect_neo, create_db as create_neo_db, load_graph, queryTwo
import sys

mongo_client = connect_mongo()
neo_client = connect_neo()

print("Welcome!\n")

open_gui = input("\nWould you like to open the GUI? (y/n): ")
if (open_gui == "y"):
    GUI(mongo_client, neo_client)
    sys.exit(0)


db_name = input("Enter a name for the database (or q to exit): ")
if (db_name == "q"): exit(0, db_name, mongo_client, neo_client)

mongo_database, new_mongo_db = create_db(mongo_client, db_name)
new_neo_db = create_neo_db(neo_client, db_name)

if (new_mongo_db or new_neo_db):
    print("\n******Before loading tsv files, please make sure the files are in the import folder for neo4j******\n")
    nodes_filename = input("\nEnter the filename for nodes (or q to exit): ")
    if (nodes_filename == "q"): exit(0, db_name, mongo_client, neo_client)

    edges_filename = input("\nEnter the filename for relationships (or q to exit): ")
    if (edges_filename == "q"): exit(0, db_name, mongo_client, neo_client)

    if (new_mongo_db):
        load_documents(mongo_database, nodes_filename, edges_filename)
    if (new_neo_db):
        load_graph(neo_client, db_name, nodes_filename, edges_filename)

while True:
    query = 0;
    print("\n1. Run query one (simple)")
    print("2. Run query two (complex)")
    print("3. Exit")
    
    while (query <= 0 or query > 3):
        query = int(input("Please enter a command: "))
    
    if (query == 3):
        exit(0, db_name, mongo_client, neo_client)
    
    if (query == 1):
        disease_id = input("\nEnter disease id: ")
        queryOne(mongo_database, disease_id)
    else:
        disease_id = input("\nEnter disease id: ")
        queryTwo(neo_client, db_name, disease_id)
