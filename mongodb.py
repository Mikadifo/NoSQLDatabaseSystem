import csv
import tkinter as tk
from models.node import Node
from models.relationship import Relationship
from pymongo import MongoClient

def connect_mongo():
    print("Connecting to mongo server...")

    mongo_client = MongoClient("mongodb://localhost:27017/")
    mongo_client.list_database_names()

    print("Connection successful!\n")

    return mongo_client

def create_db(client, db_name):
    print("Creating mongo database:", db_name, "...")
    db_list = client.list_database_names()
    if (db_name in db_list):
        print("Database already exists")
        return (client[db_name], False)

    print("Database created successfully!")
    return (client[db_name], True)

def load_documents(db, nodes_file, edges_file):
    print("Loading nodes to mongodb...")

    collection = db["nodes"]
    with open("data/" + nodes_file, newline="", encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')

        for row in reader:
            node = Node(row["id"], row["name"], row["kind"])
            collection.insert_one(node.mongo_transform())

    print("Nodes loaded successfully!\n")

    print("Loading edges to mongodb...")

    collection = db["nodes"]
    with open("data/" + edges_file, newline="", encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')

        for row in reader:
            edge = Relationship(row["source"], row["metaedge"], row["target"])
            if "D" in edge.metaedge:
                if (edge.metaedge == "CtD" or edge.metaedge == "CpD"):
                    compound = collection.find_one({"_id": edge.source})

                    collection.find_one_and_update(
                            {"_id": edge.target},
                            {"$push": {"drugs": {"_id": edge.source, "name": compound["name"]}}},
                    )
                elif (edge.metaedge == "DaG"):
                    gene = collection.find_one({"_id": edge.target})

                    collection.find_one_and_update(
                            {"_id": edge.source},
                            {"$push": {"genes": {"_id": edge.target, "name": gene["name"]}}},
                    )
                elif (edge.metaedge == "DlA"):
                    location = collection.find_one({"_id": edge.target})

                    collection.find_one_and_update(
                            {"_id": edge.source},
                            {"$push": {"locations": {"_id": edge.target, "name": location["name"]}}},
                    )

    print("Relationships loaded successfully!\n")


def queryOne(database, disease_id, root = None):
    print("Running query one...")

    collection = database["nodes"]
    result = collection.find_one({"_id": disease_id})

    gene_names=[]
    location_names=[]
    drug_names=[]

    if ("genes" in result):
        gene_names = [gene["name"] for gene in result["genes"]]
    if ("locations" in result):
        location_names = [location["name"] for location in result["locations"]]
    if ("drugs" in result):
        drug_names = [gene["name"] for gene in result["drugs"]]

    if root:
        tk.Label(root, text="Results:").pack(pady=10)

        tk.Label(root, text="Disease name:").pack(pady=10)
        tk.Label(root, text=result["name"]).pack(pady=2)

        tk.Label(root, text="Gene names that cause it:").pack(pady=10)
        genes_listbox = tk.Listbox(root, width=50)
        genes_listbox.pack(pady=2)

        for index, name in enumerate(gene_names, start=1):
            genes_listbox.insert(tk.END, f"{index}.{name}")

        tk.Label(root, text="Where it occurs:").pack(pady=10)
        locations_listbox = tk.Listbox(root, width=50)
        locations_listbox.pack(pady=2)

        for index, name in enumerate(location_names, start=1):
            locations_listbox.insert(tk.END, f"{index}.{name}")

        tk.Label(root, text="Drugs that treat/palliate it:").pack(pady=10)
        drugs_listbox = tk.Listbox(root, width=50)
        drugs_listbox.pack(pady=2)

        for index, name in enumerate(drug_names, start=1):
            drugs_listbox.insert(tk.END, f"{index}.{name}")
    else:
        print("\nResults:\n")
        print("Disease name: ", result["name"])
        print("Drugs that treat/palliate it: ", ", ".join(drug_names))
        print("Gene names that cause it: ", ", ".join(gene_names))
        print("Where it occurs: ", ", ".join(location_names), "\n")

    print("Query One completed!")
