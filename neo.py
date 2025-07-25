from models.relationship import Relationship
from neo4j import GraphDatabase
import csv
import os
import tkinter as tk
from dotenv import load_dotenv

load_dotenv()

def connect_neo():
    print("Connecting to neo4j instance...")

    neo_client = GraphDatabase.driver("neo4j://127.0.0.1:7687",  auth=("neo4j", os.getenv("PASSWORD")))
    neo_client.verify_connectivity()

    print("Connection successful!\n")

    return neo_client

def create_db(client, db_name):
    print("Creating neo4j database:", db_name, "...")
    with client.session(database="system") as session:
        result = session.run("SHOW DATABASES")
        db_list = [record["name"] for record in result]

    if (db_name in db_list):
        print("Database already exists")
        return False

    with client.session(database="system") as session:
        session.run(f"CREATE DATABASE {db_name}")
        print("Database created successfully!")
        return True

def load_graph(client, db, nodes_file, edges_file):
    print("\nLoading nodes to neo4j...")
    with client.session(database=db) as session:
        session.run(f"""
        LOAD CSV WITH HEADERS FROM 'file:///{nodes_file}' AS line FIELDTERMINATOR '\t'
        CREATE (n {{id: line.id, name: line.name, kind: line.kind}})
        """)
    with client.session(database=db) as session:
        for label in ["Disease", "Compound", "Gene", "Anatomy"]:
            session.run(f"""
            CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE;
            """)
    print("Creating labels...")
    with client.session(database=db) as session:
        session.run("""
        MATCH (n {kind: 'Disease'})
        SET n:Disease
        SET n.kind = NULL
        """)
    with client.session(database=db) as session:
        session.run("""
        MATCH (n {kind: 'Compound'})
        SET n:Compound
        SET n.kind = NULL
        """)
    with client.session(database=db) as session:
        session.run("""
        MATCH (n {kind: 'Gene'})
        SET n:Gene
        SET n.kind = NULL
        """)
    with client.session(database=db) as session:
        session.run("""
        MATCH (n {kind: 'Anatomy'})
        SET n:Anatomy
        SET n.kind = NULL
        """)
    print("Labels created")
    print("\nNodes loaded successfully!")

    print("Loading relationships to neo4j...")
    with open("data/" + edges_file, newline="", encoding='utf-8') as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter='\t')

        for row in reader:
            edge = Relationship(row["source"], row["metaedge"], row["target"])
            if (edge.metaedge[1] == "r" or
                edge.metaedge[1] == "c" or
                edge.metaedge[1] == "i" or
                edge.metaedge[1] == "b" or
                edge.metaedge[1] == "a" or
                edge.metaedge[1] == "e" or
                edge.metaedge == "DuG" or
                edge.metaedge == "DdG"
                ):
                continue

            client.execute_query("""
            MATCH (source {id: $source_id}), (target {id: $target_id})
            CREATE (source)-[rel:%s]->(target)
            """%edge.metaedge, source_id = edge.source, target_id = edge.target, database_ = db)
    print("Relationships loaded successfully!")

def queryTwo(client, db, disease_id, root = None):
    print("Running query one...")
    with client.session(database=db) as session:
        result = session.run("""
        MATCH (c:Compound)-[:CuG|CdG]->(g:Gene)
        MATCH (d:Disease {id: $disease_id})-[:DlA]->(l:Anatomy)
        WHERE
        (
            ((c)-[:CuG]->(g) AND (l)-[:AdG]->(g))
            OR
            ((c)-[:CdG]->(g) AND (l)-[:AuG]->(g))
        ) AND NOT (c)-[:CtD|CpD]->(d)
        RETURN DISTINCT c.name as drug_names
        """, {"disease_id": disease_id})

        drug_names = [record["drug_names"] for record in result]

        if root:
            tk.Label(root, text="Drug names:").pack(pady=10)
            listbox = tk.Listbox(root, width=50, height=20)
            listbox.pack(pady=5)

            for index, name in enumerate(drug_names, start=1):
                listbox.insert(tk.END, f"{index}.{name}")
        else:
            print("Drug names:\n")
            print(drug_names)

        print("Query Two completed!")
