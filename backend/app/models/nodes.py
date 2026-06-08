from datetime import date, datetime
from typing import Any
from pydantic import BaseModel


class CompanyNode(BaseModel):
    id: str | None = None
    name: str
    ticker: str | None = None
    hq_country: str | None = None
    hq_city: str | None = None
    founded_year: int | None = None
    employee_count: int | None = None
    revenue_usd_bn: float | None = None
    revenue_year: int | None = None
    segment: str | None = None
    public: bool = True
    website: str | None = None
    description: str | None = None
    source_urls: list[str] = []


class TechnologyNode(BaseModel):
    id: str | None = None
    name: str
    category: str | None = None
    generation: str | None = None
    trl: int | None = None
    description: str | None = None
    source_urls: list[str] = []


class StandardNode(BaseModel):
    id: str | None = None
    name: str
    identifier: str | None = None
    issuing_body: str | None = None
    domain: str | None = None
    status: str | None = None
    published_date: str | None = None
    version: str | None = None
    url: str | None = None
    description: str | None = None


class ProductNode(BaseModel):
    id: str | None = None
    name: str
    product_type: str | None = None
    launched_date: str | None = None
    discontinued: bool = False
    description: str | None = None
    source_urls: list[str] = []


class RegBodyNode(BaseModel):
    id: str | None = None
    name: str
    full_name: str | None = None
    type: str | None = None
    scope: str = "Global"
    founded_year: int | None = None
    website: str | None = None
    region: str = "Global"


class MarketNode(BaseModel):
    id: str | None = None
    name: str
    segment: str | None = None
    geography: str = "Global"
    size_usd_bn: float | None = None
    size_year: int | None = None
    cagr_pct: float | None = None
    forecast_year: int | None = None
    description: str | None = None


class PersonNode(BaseModel):
    id: str | None = None
    name: str
    role: str | None = None
    company_name: str | None = None
    linkedin_url: str | None = None


class EventNode(BaseModel):
    id: str | None = None
    name: str
    event_type: str | None = None
    date: str | None = None
    value_usd_bn: float | None = None
    status: str | None = None
    description: str | None = None
    source_urls: list[str] = []


class ArticleNode(BaseModel):
    id: str | None = None
    title: str
    url: str
    source: str | None = None
    published_at: str | None = None
    scraped_at: str | None = None
    processed: bool = False
    content: str | None = None


class GraphNode(BaseModel):
    id: str
    label: str
    name: str
    properties: dict[str, Any] = {}


class GraphLink(BaseModel):
    source: str
    target: str
    type: str
    properties: dict[str, Any] = {}


class GraphData(BaseModel):
    nodes: list[GraphNode]
    links: list[GraphLink]
