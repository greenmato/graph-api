from flask import Flask, request
from database import Neo4J, neo4j_connect


app = Flask(__name__)
app.config.from_pyfile('settings.cfg')


@app.route('/nodes', methods=['GET'])
def get_nodes() -> dict:
    name = request.args.get('name')

    db = neo4j_connect()
    nodes = db.get_nodes(name)
    db.close()

    nodes_list = [
        {
            'id': r[0].id,
            'name': r[0].get('message')
        } for r in nodes
    ]
    return _success({'nodes': nodes_list})

@app.route('/nodes', methods=['POST'])
def create_node() -> dict:
    db = neo4j_connect()
    node_id = db.create_node(request.form['name'])
    db.close()

    return _success({'id': node_id})

@app.route('/node/<int:node_id>', methods=['GET'])
def get_node(node_id) -> dict:
    db = neo4j_connect()
    node = db.get_node(node_id)
    db.close()

    node_dict = {
        'id': node.id,
        'name': node.get('message')
    }
    return _success({'node': node_dict})

@app.route('/node/<int:node_id>', methods=['DELETE'])
def delete_node(node_id: int) -> dict:
    db = neo4j_connect()
    node_id = db.delete_node(node_id)
    db.close()

    return _success({'id': node_id})

@app.route('/edges', methods=['POST'])
def create_edge() -> dict:
    db = neo4j_connect()
    edge_id = db.create_edge(
        int(request.form['start']),
        int(request.form['end']),
        int(request.form['cost'])
    )
    db.close()

    return _success({'id': edge_id})

@app.route('/edges', methods=['DELETE'])
def delete_edge() -> dict:
    db = neo4j_connect()
    edge_id = db.delete_edge(
        int(request.form['start']), int(request.form['end']))
    db.close()

    return _success({'id': edge_id})

@app.route('/shortest-path', methods=['GET'])
def shortest_path() -> dict:
    db = neo4j_connect()
    path = db.shortest_path(
        int(request.form['start']), int(request.form['end']))
    db.close()

    path_list = [
        {
            'node': {
                'id': r[0],
                'name': r[1]
            },
            'total_cost': r[2]
        } for r in path
    ]
    return _success({'path': path_list})

def _success(data: dict) -> dict:
    return {
        'success': True,
        'data': data
    }
