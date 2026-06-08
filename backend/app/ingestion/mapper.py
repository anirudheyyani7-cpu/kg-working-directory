import logging
from datetime import datetime
from neo4j import AsyncDriver
from rapidfuzz import process as fuzz_process
from app.config import settings
from app.models.relationships import ExtractionResult, ArticleIngestion
from app.seed.companies import COMPANIES
from app.seed.standards import STANDARDS
from app.seed.technologies import TECHNOLOGIES

logger = logging.getLogger(__name__)

_canonical_names: dict[str, list[str]] = {}


def _build_canonical_index():
    if _canonical_names:
        return
    _canonical_names["Company"] = [c["name"] for c in COMPANIES]
    _canonical_names["Standard"] = [s["name"] for s in STANDARDS]
    _canonical_names["Technology"] = [t["name"] for t in TECHNOLOGIES]


def _normalize_name(name: str, entity_type: str) -> str:
    _build_canonical_index()
    candidates = _canonical_names.get(entity_type)
    if not candidates:
        return name
    match = fuzz_process.extractOne(name, candidates, score_cutoff=90)
    return match[0] if match else name


async def map_to_graph(
    result: ExtractionResult,
    article: ArticleIngestion,
    driver: AsyncDriver,
) -> int:
    threshold = settings.confidence_threshold
    new_relationships = 0

    filtered_entities = [e for e in result.entities if e.confidence >= threshold]
    filtered_rels = [r for r in result.relationships if r.confidence >= threshold]

    if not filtered_entities and not filtered_rels:
        return 0

    async with driver.session() as session:
        for entity in filtered_entities:
            canonical = _normalize_name(entity.name, entity.type)
            props = {**entity.properties, "name": canonical, "updated_at": datetime.utcnow().isoformat()}
            await session.run(
                f"MERGE (n:{entity.type} {{name: $name}}) SET n += $props",
                name=canonical, props=props,
            )

        for rel in filtered_rels:
            src_name = _normalize_name(rel.source_name, rel.source_type)
            tgt_name = _normalize_name(rel.target_name, rel.target_type)
            try:
                await session.run(
                    f"""
                    MERGE (src:{rel.source_type} {{name: $src_name}})
                    MERGE (tgt:{rel.target_type} {{name: $tgt_name}})
                    MERGE (src)-[r:{rel.relationship_type}]->(tgt)
                    SET r += $props, r.last_seen = date(), r.source_article = $url
                    """,
                    src_name=src_name, tgt_name=tgt_name,
                    props=rel.properties or {}, url=article.url,
                )
                new_relationships += 1
            except Exception as e:
                logger.warning(f"Failed to write relationship {rel.relationship_type}: {e}")

        # Only create Article node when new relationships were found (preserves Aura node limit)
        if new_relationships > 0 and article.url:
            await session.run(
                """
                MERGE (a:Article {url: $url})
                SET a.title = $title, a.source = $source,
                    a.published_at = $published_at, a.processed = true,
                    a.scraped_at = $scraped_at
                """,
                url=article.url, title=article.title, source=article.source,
                published_at=article.published_at,
                scraped_at=datetime.utcnow().isoformat(),
            )
            for entity in filtered_entities:
                canonical = _normalize_name(entity.name, entity.type)
                await session.run(
                    f"""
                    MATCH (a:Article {{url: $url}})
                    MATCH (n:{entity.type} {{name: $name}})
                    MERGE (a)-[:MENTIONS]->(n)
                    """,
                    url=article.url, name=canonical,
                )

    return new_relationships
