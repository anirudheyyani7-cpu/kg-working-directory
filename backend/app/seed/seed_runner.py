"""
Run with: python -m app.seed.seed_runner
Idempotent — safe to run multiple times. Uses MERGE so no duplicates.
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from neo4j import AsyncGraphDatabase
from app.config import settings
from app.seed.companies import COMPANIES
from app.seed.standards import REG_BODIES, STANDARDS
from app.seed.technologies import TECHNOLOGIES, MARKETS
from app.seed.relationships import RELATIONSHIPS, EVENTS, PRODUCTS


async def run_schema(session):
    schema_path = os.path.join(os.path.dirname(__file__), "schema.cypher")
    with open(schema_path) as f:
        statements = [s.strip() for s in f.read().split(";") if s.strip()]
    for stmt in statements:
        try:
            await session.run(stmt)
        except Exception as e:
            if "already exists" not in str(e).lower() and "equivalent" not in str(e).lower():
                print(f"  Schema warning: {e}")


async def seed_companies(session):
    count = 0
    for c in COMPANIES:
        props = {k: v for k, v in c.items()}
        await session.run(
            "MERGE (n:Company {name: $name}) SET n += $props",
            name=c["name"], props=props,
        )
        count += 1
    print(f"  Companies: {count} upserted")


async def seed_reg_bodies(session):
    count = 0
    for rb in REG_BODIES:
        props = {k: v for k, v in rb.items()}
        await session.run(
            "MERGE (n:RegBody {name: $name}) SET n += $props",
            name=rb["name"], props=props,
        )
        count += 1
    print(f"  RegBodies: {count} upserted")


async def seed_standards(session):
    count = 0
    for s in STANDARDS:
        props = {k: v for k, v in s.items()}
        await session.run(
            "MERGE (n:Standard {name: $name}) SET n += $props",
            name=s["name"], props=props,
        )
        count += 1
    print(f"  Standards: {count} upserted")


async def seed_technologies(session):
    count = 0
    for t in TECHNOLOGIES:
        props = {k: v for k, v in t.items()}
        await session.run(
            "MERGE (n:Technology {name: $name}) SET n += $props",
            name=t["name"], props=props,
        )
        count += 1
    for m in MARKETS:
        props = {k: v for k, v in m.items()}
        await session.run(
            "MERGE (n:Market {name: $name}) SET n += $props",
            name=m["name"], props=props,
        )
        count += 1
    print(f"  Technologies + Markets: {count} upserted")


async def seed_products(session):
    count = 0
    for p in PRODUCTS:
        props = {k: v for k, v in p.items() if k not in ("maker", "implements", "uses_tech")}
        await session.run(
            "MERGE (n:Product {name: $name}) SET n += $props",
            name=p["name"], props=props,
        )
        await session.run(
            """
            MATCH (maker:Company {name: $maker})
            MATCH (prod:Product {name: $product})
            MERGE (maker)-[:MAKES]->(prod)
            """,
            maker=p["maker"], product=p["name"],
        )
        for std_name in p.get("implements", []):
            await session.run(
                """
                MATCH (prod:Product {name: $product})
                MATCH (std:Standard {name: $std})
                MERGE (prod)-[:IMPLEMENTS]->(std)
                """,
                product=p["name"], std=std_name,
            )
        for tech_name in p.get("uses_tech", []):
            await session.run(
                """
                MATCH (prod:Product {name: $product})
                MATCH (tech:Technology {name: $tech})
                MERGE (prod)-[:USES_TECHNOLOGY]->(tech)
                """,
                product=p["name"], tech=tech_name,
            )
        count += 1
    print(f"  Products: {count} upserted")


async def seed_relationships(session):
    count = 0
    for rel in RELATIONSHIPS:
        query = f"""
            MERGE (src:{rel['source_label']} {{name: $src_name}})
            MERGE (tgt:{rel['target_label']} {{name: $tgt_name}})
            MERGE (src)-[r:{rel['type']}]->(tgt)
            SET r += $props
        """
        await session.run(query, src_name=rel["source"], tgt_name=rel["target"], props=rel.get("props", {}))
        count += 1
    print(f"  Relationships: {count} upserted")


async def seed_events(session):
    count = 0
    for ev in EVENTS:
        props = {k: v for k, v in ev.items() if k != "involves"}
        await session.run(
            "MERGE (n:Event {name: $name}) SET n += $props",
            name=ev["name"], props=props,
        )
        for company_name in ev.get("involves", []):
            await session.run(
                """
                MATCH (ev:Event {name: $event_name})
                MERGE (c:Company {name: $company_name})
                MERGE (ev)-[:INVOLVES]->(c)
                """,
                event_name=ev["name"], company_name=company_name,
            )
        count += 1
    print(f"  Events: {count} upserted")


async def print_counts(session):
    labels = ["Company", "Technology", "Standard", "Product", "RegBody", "Market", "Event"]
    total_nodes = 0
    for label in labels:
        result = await session.run(f"MATCH (n:{label}) RETURN count(n) AS cnt")
        record = await result.single()
        cnt = record["cnt"]
        total_nodes += cnt
        print(f"  {label}: {cnt}")
    result = await session.run("MATCH ()-[r]->() RETURN count(r) AS cnt")
    record = await result.single()
    print(f"  Total relationships: {record['cnt']}")
    print(f"  Total nodes: {total_nodes}")


async def main():
    print("Connecting to Neo4j...")
    driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_username, settings.neo4j_password),
    )
    async with driver.session() as session:
        print("Setting up schema...")
        await run_schema(session)
        print("Seeding data...")
        await seed_companies(session)
        await seed_reg_bodies(session)
        await seed_standards(session)
        await seed_technologies(session)
        await seed_products(session)
        await seed_relationships(session)
        await seed_events(session)
        print("\nFinal counts:")
        await print_counts(session)
    await driver.close()
    print("\nSeed complete.")


if __name__ == "__main__":
    asyncio.run(main())
