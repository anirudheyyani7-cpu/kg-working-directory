import anthropic
from app.config import settings
from app.models.relationships import ExtractionResult, ExtractionEntity, ExtractionRelationship

SYSTEM_PROMPT = """You are a knowledge graph extraction engine for the Telecom, Media & Technology (TMT) domain.

Extract structured entities and relationships from the provided article text.
Focus ONLY on named entities that fit these exact types:

ENTITY TYPES:
- Company: named telecom operators, vendors, media companies, chipmakers, hyperscalers
- Technology: named technologies, protocols, network functions (e.g. "Massive MIMO", "Network Slicing")
- Standard: named specs or releases (e.g. "3GPP Release 17", "MPEG-DASH", "IEEE 802.11ax")
- Product: named products or platforms (e.g. "Ericsson Radio System", "Nokia AirScale")
- RegBody: standards bodies, regulators, industry associations
- Person: named executives or technical leaders with clear company affiliation
- Event: M&A deals, product launches, spectrum auctions, partnerships — only if explicitly stated
- Market: named market segments (e.g. "Private 5G", "FAST Channels")

RELATIONSHIP TYPES (use ONLY these exact strings):
ACQUIRED, PARTNERED_WITH, COMPETES_WITH, INVESTED_IN, MAKES, IMPLEMENTS,
CONTRIBUTED_TO, ISSUED_BY, SUPERSEDES, DEFINES, ENABLES, REQUIRES,
MEMBER_OF, LEADS, INVOLVES, AFFECTS, SUPPLIES_TO, USES_TECHNOLOGY

Rules:
- Only extract entities explicitly named in the text
- Only extract relationships with clear textual evidence
- Assign confidence 0.0-1.0 to each extraction
- Do not infer or hallucinate relationships not stated in the text
- For Events, include date (YYYY-MM-DD) and value_usd_bn if mentioned"""

EXTRACTION_TOOL = {
    "name": "extract_tmt_entities",
    "description": "Extract TMT entities and relationships from article text",
    "input_schema": {
        "type": "object",
        "properties": {
            "entities": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["Company", "Technology", "Standard", "Product", "RegBody", "Person", "Event", "Market"]},
                        "name": {"type": "string"},
                        "properties": {"type": "object", "additionalProperties": True},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    },
                    "required": ["type", "name", "confidence"],
                },
            },
            "relationships": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "source_name": {"type": "string"},
                        "source_type": {"type": "string"},
                        "relationship_type": {"type": "string"},
                        "target_name": {"type": "string"},
                        "target_type": {"type": "string"},
                        "properties": {"type": "object", "additionalProperties": True},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "evidence": {"type": "string"},
                    },
                    "required": ["source_name", "source_type", "relationship_type", "target_name", "target_type", "confidence"],
                },
            },
        },
        "required": ["entities", "relationships"],
    },
}


async def extract_entities(content: str, title: str, source: str) -> ExtractionResult:
    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    response = await client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        tools=[EXTRACTION_TOOL],
        tool_choice={"type": "tool", "name": "extract_tmt_entities"},
        messages=[{
            "role": "user",
            "content": f"Article from {source}:\n\nTitle: {title}\n\n{content[:8000]}",
        }],
    )
    tool_block = next((b for b in response.content if b.type == "tool_use"), None)
    if not tool_block:
        return ExtractionResult()
    data = tool_block.input
    entities = [ExtractionEntity(**e) for e in data.get("entities", [])]
    relationships = [ExtractionRelationship(**r) for r in data.get("relationships", [])]
    return ExtractionResult(entities=entities, relationships=relationships)
