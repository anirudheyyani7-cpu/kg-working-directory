from neo4j import AsyncDriver
from app.models.nodes import GraphNode, GraphLink, GraphData


def _sanitize(value):
    """Convert Neo4j-specific types to JSON-serializable Python types."""
    import neo4j.time
    if isinstance(value, (neo4j.time.Date, neo4j.time.DateTime, neo4j.time.Time, neo4j.time.Duration)):
        return str(value)
    if isinstance(value, dict):
        return {k: _sanitize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize(v) for v in value]
    return value


def _sanitize_props(props: dict) -> dict:
    return {k: _sanitize(v) for k, v in props.items()}


def _to_graph_node(record_node) -> GraphNode:
    labels = list(record_node.labels)
    label = labels[0] if labels else "Unknown"
    props = _sanitize_props(dict(record_node.items()))
    return GraphNode(
        id=props.get("id", str(record_node.element_id)),
        label=label,
        name=props.get("name", ""),
        properties={k: v for k, v in props.items() if k not in ("id",)},
    )


async def get_node(driver: AsyncDriver, node_id: str) -> dict | None:
    async with driver.session() as session:
        result = await session.run(
            "MATCH (n) WHERE n.id = $id OR elementId(n) = $id RETURN n LIMIT 1",
            id=node_id,
        )
        record = await result.single()
        if not record:
            return None
        node = record["n"]
        labels = list(node.labels)
        props = _sanitize_props(dict(node.items()))
        return {"id": props.get("id", str(node.element_id)), "label": labels[0] if labels else "Unknown", **props}


async def get_neighbors(
    driver: AsyncDriver, node_id: str, depth: int = 1, node_types: list[str] | None = None
) -> GraphData:
    type_filter = ""
    if node_types:
        labels = "|".join(node_types)
        type_filter = f"AND (any(l IN labels(n) WHERE l IN {node_types!r}))"

    query = f"""
        MATCH path = (start)-[r*1..{depth}]-(n)
        WHERE (start.id = $id OR elementId(start) = $id)
        AND NOT n:Article {type_filter}
        RETURN start, relationships(path) AS rels, nodes(path) AS path_nodes
        LIMIT 200
    """
    async with driver.session() as session:
        result = await session.run(query, id=node_id)
        nodes_map: dict[str, GraphNode] = {}
        links: list[GraphLink] = []
        async for record in result:
            for node in record["path_nodes"]:
                props = _sanitize_props(dict(node.items()))
                nid = props.get("id", str(node.element_id))
                if nid not in nodes_map:
                    nodes_map[nid] = _to_graph_node(node)
            for rel in record["rels"]:
                src = dict(rel.start_node.items())
                tgt = dict(rel.end_node.items())
                src_id = src.get("id", str(rel.start_node.element_id))
                tgt_id = tgt.get("id", str(rel.end_node.element_id))
                links.append(GraphLink(source=src_id, target=tgt_id, type=rel.type, properties=dict(rel.items())))
    return GraphData(nodes=list(nodes_map.values()), links=links)


async def get_shortest_path(driver: AsyncDriver, from_id: str, to_id: str) -> GraphData:
    query = """
        MATCH path = shortestPath(
            (a)-[*..6]-(b)
        )
        WHERE (a.id = $from_id OR elementId(a) = $from_id)
        AND (b.id = $to_id OR elementId(b) = $to_id)
        RETURN nodes(path) AS path_nodes, relationships(path) AS rels
        LIMIT 1
    """
    async with driver.session() as session:
        result = await session.run(query, from_id=from_id, to_id=to_id)
        record = await result.single()
        if not record:
            return GraphData(nodes=[], links=[])
        nodes = [_to_graph_node(n) for n in record["path_nodes"]]
        links = []
        for rel in record["rels"]:
            src = dict(rel.start_node.items())
            tgt = dict(rel.end_node.items())
            src_id = src.get("id", str(rel.start_node.element_id))
            tgt_id = tgt.get("id", str(rel.end_node.element_id))
            links.append(GraphLink(source=src_id, target=tgt_id, type=rel.type, properties=dict(rel.items())))
        return GraphData(nodes=nodes, links=links)


async def get_subgraph_by_label(driver: AsyncDriver, label: str, limit: int = 50) -> GraphData:
    valid_labels = {"Company", "Technology", "Standard", "Product", "RegBody", "Market", "Person", "Event"}
    if label not in valid_labels:
        return GraphData(nodes=[], links=[])
    query = f"""
        MATCH (n:{label})
        OPTIONAL MATCH (n)-[r]-(m:{label})
        RETURN n, r, m
        LIMIT {limit}
    """
    async with driver.session() as session:
        result = await session.run(query)
        nodes_map: dict[str, GraphNode] = {}
        links: list[GraphLink] = []
        async for record in result:
            for node in [record["n"], record["m"]]:
                if node is None:
                    continue
                props = _sanitize_props(dict(node.items()))
                nid = props.get("id", str(node.element_id))
                if nid not in nodes_map:
                    nodes_map[nid] = _to_graph_node(node)
            rel = record["r"]
            if rel:
                src = dict(rel.start_node.items())
                tgt = dict(rel.end_node.items())
                src_id = src.get("id", str(rel.start_node.element_id))
                tgt_id = tgt.get("id", str(rel.end_node.element_id))
                links.append(GraphLink(source=src_id, target=tgt_id, type=rel.type, properties=dict(rel.items())))
        return GraphData(nodes=list(nodes_map.values()), links=links)


async def get_taxonomy(driver: AsyncDriver) -> dict:
    query = """
        MATCH (t:Technology)
        OPTIONAL MATCH (t)-[:ENABLES]->(sub:Technology)
        RETURN t.name AS name, t.category AS category, t.generation AS generation,
               collect(sub.name) AS enables
        ORDER BY t.category, t.name
    """
    async with driver.session() as session:
        result = await session.run(query)
        records = [r.data() async for r in result]
    categories: dict[str, list] = {}
    for r in records:
        cat = r.get("category") or "Other"
        categories.setdefault(cat, []).append({
            "name": r["name"],
            "generation": r.get("generation"),
            "enables": r.get("enables", []),
        })
    return {"categories": categories}


async def get_competitors(driver: AsyncDriver, company_id: str) -> list[dict]:
    query = """
        MATCH (c:Company)-[:COMPETES_WITH]-(rival:Company)
        WHERE c.id = $id OR c.name = $id
        OPTIONAL MATCH (rival)-[acq:ACQUIRED]->(target:Company)
        OPTIONAL MATCH (rival)-[:MAKES]->(p:Product)
        RETURN rival.name AS name, rival.revenue_usd_bn AS revenue,
               rival.segment AS segment, rival.hq_country AS country,
               collect(DISTINCT target.name) AS acquisitions,
               collect(DISTINCT p.name) AS products
        ORDER BY rival.revenue_usd_bn DESC NULLS LAST
    """
    async with driver.session() as session:
        result = await session.run(query, id=company_id)
        return [r.data() async for r in result]


async def get_events(driver: AsyncDriver, event_type: str | None = None, since_date: str | None = None) -> list[dict]:
    where_clauses = []
    params: dict = {}
    if event_type:
        where_clauses.append("ev.event_type = $event_type")
        params["event_type"] = event_type
    if since_date:
        where_clauses.append("ev.date >= $since_date")
        params["since_date"] = since_date
    where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    query = f"""
        MATCH (ev:Event)
        {where}
        OPTIONAL MATCH (ev)-[:INVOLVES]->(c:Company)
        RETURN ev.name AS name, ev.event_type AS event_type,
               ev.date AS date, ev.value_usd_bn AS value_usd_bn,
               ev.status AS status, ev.description AS description,
               collect(c.name) AS companies
        ORDER BY ev.date DESC
        LIMIT 100
    """
    async with driver.session() as session:
        result = await session.run(query, params)
        return [r.data() async for r in result]


async def get_standards(driver: AsyncDriver, body: str | None = None, status: str | None = None) -> list[dict]:
    where_clauses = []
    params: dict = {}
    if body:
        where_clauses.append("s.issuing_body = $body")
        params["body"] = body
    if status:
        where_clauses.append("s.status = $status")
        params["status"] = status
    where = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    query = f"""
        MATCH (s:Standard)
        {where}
        RETURN s.name AS name, s.identifier AS identifier, s.issuing_body AS issuing_body,
               s.status AS status, s.published_date AS published_date, s.description AS description
        ORDER BY s.issuing_body, s.published_date DESC
    """
    async with driver.session() as session:
        result = await session.run(query, params)
        return [r.data() async for r in result]


async def get_standard_implementors(driver: AsyncDriver, standard_id: str) -> list[dict]:
    query = """
        MATCH (s:Standard)
        WHERE s.id = $id OR s.name = $id OR s.identifier = $id
        MATCH (p:Product)-[impl:IMPLEMENTS]->(s)
        MATCH (c:Company)-[:MAKES]->(p)
        RETURN c.name AS company, p.name AS product,
               impl.compliance_level AS compliance_level
        ORDER BY c.name
    """
    async with driver.session() as session:
        result = await session.run(query, id=standard_id)
        return [r.data() async for r in result]
