from flask import current_app as app
from neo4j import GraphDatabase


class Neo4J:
    def __init__(self, uri: str, user: str, password: str) -> None:
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self) -> None:
        self._driver.close()

    def get_nodes(self, message: str) -> dict:
        with self._driver.session() as session:
            node = session.write_transaction(self._get_nodes, message)
        return node

    def get_node(self, node_id: str) -> dict:
        with self._driver.session() as session:
            node = session.write_transaction(self._get_node, node_id)
        return node

    def create_node(self, message: str) -> int:
        with self._driver.session() as session:
            node_id = session.write_transaction(self._create_node, message)
        return node_id

    def delete_node(self, node_id: str) -> str:
        with self._driver.session() as session:
            node_id = session.write_transaction(self._delete_node, node_id)
        return node_id

    def create_edge(self, start: int, end: int, cost: int) -> int:
        with self._driver.session() as session:
            edge_id = session.write_transaction(
                self._create_edge, start, end, cost)
        return edge_id

    def delete_edge(self, start: int, end: int) -> int:
        with self._driver.session() as session:
            edge_id = session.write_transaction(self._delete_edge, start, end)
        return edge_id

    def shortest_path(self, start: int, end: int) -> list:
        with self._driver.session() as session:
            edge_id = session.write_transaction(self._shortest_path, start, end)
        return edge_id

    @staticmethod
    def _get_nodes(tx, message: str) -> list:
        where = "WHERE a.message = $message " if message else ""
        result = tx.run("MATCH (a) "
                        + where
                        + "RETURN a ", message=message)
        return result.records()

    @staticmethod
    def _get_node(tx, node_id: str) -> dict:
        result = tx.run("MATCH (a) "
                        "WHERE ID(a) = $node_id "
                        "RETURN a ", node_id=node_id)
        return result.single()[0]

    @staticmethod
    def _create_node(tx, message: str) -> str:
        result = tx.run("CREATE (a:Node) "
                        "SET a.message = $message "
                        "RETURN ID(a)", message=message)
        return result.single()[0]

    @staticmethod
    def _delete_node(tx, node_id: str) -> str:
        result = tx.run("MATCH (a:Node) where ID(a) = $node_id "
                        "OPTIONAL MATCH (a)-[r]-() "
                        "DELETE r,a "
                        "RETURN ID(a)", node_id=node_id)
        return result.single()[0]

    @staticmethod
    def _create_edge(tx, start: int, end: int, cost: int) -> str:
        result = tx.run("MATCH (a:Node),(b:Node) "
                        "WHERE ID(a) = $start AND ID(b) = $end "
                        "CREATE (a)-[r:CONNECTION {cost:$cost}]->(b) "
                        "RETURN ID(r)", start=start, end=end, cost=cost)
        return result.single()[0]

    @staticmethod
    def _delete_edge(tx, start: int, end: int) -> str:
        result = tx.run("MATCH (a:Node)-[r:CONNECTION]-(b:Node) "
                        "WHERE ID(a) = $start AND ID(b) = $end "
                        "DELETE r "
                        "RETURN ID(r)", start=start, end=end)
        return result.single()[0]

    @staticmethod
    def _shortest_path(tx, start: int, end: int) -> list:
        result = tx.run("MATCH (a:Node), (b:Node) "
                        "WHERE ID(a) = $start AND ID(b) = $end "
                        "CALL algo.shortestPath.stream(a, b, 'cost') "
                        "YIELD nodeId, cost "
                        "MATCH (other:Node) WHERE id(other) = nodeId "
                        "RETURN ID(other) AS id, other.message, cost ",
                        start=start, end=end)
        return result.records()


def neo4j_connect() -> Neo4J:
    return Neo4J(
        app.config['DB_HOST'], app.config['DB_USER'], app.config['DB_PASS'])
