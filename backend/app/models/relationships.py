from typing import Any
from pydantic import BaseModel


class GraphEdge(BaseModel):
    source_id: str
    target_id: str
    type: str
    properties: dict[str, Any] = {}


class ExtractionEntity(BaseModel):
    type: str
    name: str
    properties: dict[str, Any] = {}
    confidence: float


class ExtractionRelationship(BaseModel):
    source_name: str
    source_type: str
    relationship_type: str
    target_name: str
    target_type: str
    properties: dict[str, Any] = {}
    confidence: float
    evidence: str | None = None


class ExtractionResult(BaseModel):
    entities: list[ExtractionEntity] = []
    relationships: list[ExtractionRelationship] = []


class ArticleIngestion(BaseModel):
    title: str
    url: str = ""
    source: str = "manual"
    published_at: str | None = None
    content: str
