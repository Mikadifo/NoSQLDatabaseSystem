import tkinter as tk

from mongodb import create_db, load_documents, queryOne
from neo import create_db as create_neo_db, load_graph, queryTwo

root = None
mongo_client = None
mongo_database = None
neo_client = None
db_name = None

def GUI(mongo, neo):
    global root, mongo_client, neo_client

    mongo_client = mongo
    neo_client = neo

    root = tk.Tk()
    root.geometry("")
    root.resizable(True, True)
    root.title("Database System")

    tk.Label(root, text="Database Name:").pack(pady=10)
    entry = tk.Entry(root)
    entry.pack(pady=5)

    tk.Button(root, text="Submit", command=lambda: create_database(entry)).pack(pady=10)

    root.update()

    root.mainloop()

def create_database(entry):
    global root, mongo_client, neo_client, mongo_database, db_name

    db_name = entry.get()

    if not db_name:
        entry.focus_set()
        return None

    mongo_database, new_mongo_db = create_db(mongo_client, db_name)
    new_neo_db = create_neo_db(neo_client, db_name)

    clear()

    if (new_mongo_db or new_neo_db):
        tk.Label(root, text="****** Before loading tsv files ******").pack(pady=5)
        tk.Label(root, text="please make sure the files are in the import folder for neo4j").pack(pady=1)

        tk.Label(root, text="Filename for nodes:").pack(pady=10)
        nodes_entry = tk.Entry(root)
        nodes_entry.pack(pady=2)

        tk.Label(root, text="Filename for edges:").pack(pady=10)
        edges_entry = tk.Entry(root)
        edges_entry.pack(pady=2)

        tk.Button(root, text="Load Data", command=lambda: load_data(nodes_entry, edges_entry, new_mongo_db, new_neo_db)).pack(pady=10)

        root.update()
    else:
        queries()

def load_data(nodes_entry, edges_entry, load_mongo, load_neo):
    global root, mongo_client, neo_client, mongo_database, db_name

    nodes_filename = nodes_entry.get()
    edges_filename = edges_entry.get()

    if not nodes_filename:
        nodes_entry.focus_set()
        return None

    if not edges_filename:
        edges_entry.focus_set()
        return None

    clear()

    if (load_mongo):
        tk.Label(root, text="Loading data to mongodb...").pack(pady=10)
        load_documents(mongo_database, nodes_filename, edges_filename)
        tk.Label(root, text="Data loaded correctly...").pack(pady=10)

    if (load_neo):
        tk.Label(root, text="Loading data to neo4j...").pack(pady=10)
        load_graph(neo_client, db_name, nodes_filename, edges_filename)
        tk.Label(root, text="Data loaded correctly...").pack(pady=10)

    queries()

def queries():
    global root, mongo_client, neo_client, mongo_database

    clear()

    tk.Label(root, text="Select a query").pack(pady=10)
    tk.Button(root, text="Query 1 (simple)", command=lambda: get_disease_id(1)).pack(pady=10)
    tk.Button(root, text="Query 2 (complex)", command=lambda: get_disease_id(2)).pack(pady=10)
     
    root.update()

def get_disease_id(query_target):
    global root

    clear()

    tk.Label(root, text="Disease Id:").pack(pady=10)
    entry = tk.Entry(root)
    entry.pack(pady=5)

    tk.Button(root, text="Run Query", command=lambda: run_query(entry, query_target)).pack(pady=10)

    root.update()

def run_query(entry, query):
    global root, mongo_database, neo_client, db_name

    disease_id = entry.get()

    if not disease_id:
        entry.focus_set()
        return None

    clear()

    if query == 1:
        queryOne(mongo_database, disease_id,  root)
    else:
        queryTwo(neo_client, db_name, disease_id, root)

    tk.Button(root, text="Run Another Query", command=queries).pack(pady=20)

    root.update()

def clear():
    global root

    for widget in root.winfo_children():
        widget.destroy()
