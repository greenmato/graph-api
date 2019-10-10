# Graph API

Small API service written with Python's Flask framework that performs basic CRUD and shortest path algorithm on a Neo4J graph database.

Requirements:
* Python 3.6
* Neo4J 3.5 + algorithms plugin

Setup:
* `pip install -r requirements.txt`

To run locally:
* `sudo neo4j start`
* `export FLASK_APP=graph_api.py`
* `flask run`
