from neo4j import AsyncDriver


async def search_entities(
    driver: AsyncDriver, query: str, labels: list[str] | None = None, limit: int = 20
) -> list[dict]:
    label_filter = ""
    params: dict = {"query": query + "~", "limit": limit}

    if labels:
        label_filter = f"AND any(l IN labels(n) WHERE l IN {labels!r})"

    cypher = f"""
        CALL db.index.fulltext.queryNodes('entity_search', $query)
        YIELD node AS n, score
        WHERE NOT n:Article {label_filter}
        RETURN elementId(n) AS id,
               [l IN labels(n) | l][0] AS label,
               n.name AS name,
               score,
               properties(n) AS properties
        ORDER BY score DESC
        LIMIT $limit
    """
    async with driver.session() as session:
        result = await session.run(cypher, params)
        return [r.data() async for r in result]
