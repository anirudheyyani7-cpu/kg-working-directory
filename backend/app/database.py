from neo4j import AsyncGraphDatabase, AsyncDriver
from app.config import settings

_driver: AsyncDriver | None = None


async def get_driver() -> AsyncDriver:
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_username, settings.neo4j_password),
            max_connection_pool_size=50,
        )
    return _driver


async def close_driver():
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None


async def run_query(query: str, params: dict = None) -> list[dict]:
    driver = await get_driver()
    async with driver.session() as session:
        result = await session.run(query, params or {})
        return [record.data() async for record in result]


async def setup_schema():
    schema_path = __file__.replace("database.py", "seed/schema.cypher")
    try:
        with open(schema_path) as f:
            statements = [s.strip() for s in f.read().split(";") if s.strip()]
        driver = await get_driver()
        async with driver.session() as session:
            for stmt in statements:
                try:
                    await session.run(stmt)
                except Exception:
                    pass  # index may already exist
    except FileNotFoundError:
        pass
