# TMT Knowledge Graph

> A full-stack, self-sustaining knowledge graph for the **Telecom, Media & Technology** domain — track companies, standards, technologies, competitive moves, and M&A in one interactive graph that automatically grows from live news feeds.

---

## What's Inside

| Area | Description |
|---|---|
| **Relationship Explorer** | Force-directed graph — click nodes to expand neighbors, navigate connections between companies, standards, and technologies |
| **Domain Taxonomy** | Hierarchical cytoscape tree of TMT sub-domains (RAN, Core, Edge, Media, AI/ML, Transport) |
| **Competitive Intelligence** | M&A timeline, partnerships, and market position dashboard |
| **Standards Tracker** | 3GPP, ITU, ETSI, O-RAN, IEEE specs mapped to issuing bodies, status, and vendor implementations |
| **Ingest Panel** | Paste any article → Claude extracts entities & relationships → writes to graph. Or trigger RSS feed poll manually |

---

## Architecture

```
RSS Feeds (13 sources)
    │
    ▼
FastAPI Worker (Railway)
  - feedparser polls feeds every 4h
  - httpx fetches full article text
  - Claude API (tool_use) extracts entities + relationships
  - rapidfuzz normalizes names to canonical seed values
  - Neo4j MERGE writes (confidence ≥ 0.75 only)
    │
    ▼
Neo4j Aura Free ◄──── FastAPI Read API (Railway)
                              │
                              ▼
                     Next.js Frontend (Vercel)
                       - react-force-graph (explorer)
                       - cytoscape + dagre (taxonomy)
                       - Ingest panel (manual extraction)
```

---

## Tech Stack

### Backend (`/backend`)
| Package | Purpose |
|---|---|
| FastAPI + uvicorn | Async API server |
| neo4j (Python driver) | Graph database client |
| anthropic | Claude API for LLM entity extraction |
| feedparser | RSS/Atom feed parsing |
| httpx + beautifulsoup4 | Article scraping |
| APScheduler | Ingestion cron (every 4h) |
| upstash-redis | URL deduplication + caching |
| rapidfuzz | Entity name normalization |
| pydantic v2 | Data validation |

### Frontend (`/frontend`)
| Package | Purpose |
|---|---|
| Next.js 14 (App Router) | Framework |
| react-force-graph | WebGL force-directed graph (explorer view) |
| cytoscape.js + cytoscape-dagre | Hierarchical taxonomy tree |
| Tailwind CSS | Styling |
| Zustand | Graph state management |

### Infrastructure
| Service | Role | Free tier |
|---|---|---|
| Neo4j Aura Free | Graph database | 200k nodes, forever free |
| Upstash Redis | URL dedup + caching | 10k requests/day |
| Railway | FastAPI + scheduler | $5/month credit |
| Vercel | Next.js frontend | Hobby plan free |

---

## Getting Started

### Prerequisites
- Python 3.12+
- Node.js 20+
- Accounts: [Neo4j Aura Free](https://neo4j.com/cloud/platform/aura-graph-database/), [Upstash](https://upstash.com/), [Railway](https://railway.app/), [Vercel](https://vercel.com/)
- Anthropic API key

### 1. Backend setup

```bash
cd backend

# Install dependencies (using uv)
pip install uv
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your Neo4j Aura URI, password, Upstash URL/token, Anthropic key

# Load seed data into Neo4j (~200 nodes, ~400 relationships)
python -m app.seed.seed_runner

# Start the API server
uvicorn app.main:app --reload --port 8000
```

API docs available at `http://localhost:8000/docs`

### 2. Frontend setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000

# Start dev server
npm run dev
```

Frontend available at `http://localhost:3000`

---

## Graph Data Model

### Node Types

| Label | Key Properties |
|---|---|
| **Company** | name, segment, hq_country, revenue_usd_bn, employee_count |
| **Technology** | name, category (RAN/Core/Edge/Transport/Media/AI), generation (5G/4G/Fixed) |
| **Standard** | name, identifier, issuing_body, status (Frozen/Stable/Draft) |
| **Product** | name, product_type (Hardware/Software/Platform) |
| **RegBody** | name, type (Standards/Regulatory/Industry Assoc), scope |
| **Market** | name, segment, size_usd_bn, cagr_pct |
| **Event** | name, event_type (M&A/Partnership/Launch), date, value_usd_bn |
| **Article** | url, title, source (provenance, only written when new relationships found) |

### Relationship Types
`COMPETES_WITH` · `ACQUIRED` · `PARTNERED_WITH` · `INVESTED_IN` · `SUPPLIES_TO`  
`MEMBER_OF` · `CHAIRS` · `MAKES` · `IMPLEMENTS` · `USES_TECHNOLOGY`  
`ISSUED_BY` · `SUPERSEDES` · `DEFINES` · `CONTRIBUTED_TO`  
`ENABLES` · `REQUIRES` · `USED_IN` · `LEADS` · `INVOLVES` · `MENTIONS`

### Seed Data (pre-loaded)
- **~65 companies**: RAN vendors, operators (US/EU/Asia), hyperscalers, media, chipmakers, satellite, CDN
- **14 standards bodies**: 3GPP, ITU-T/R, ETSI, GSMA, IEEE, IETF, O-RAN Alliance, TM Forum, Alliance for Open Media, SMPTE, ATSC, BBF, DVB
- **28 standards**: 3GPP Rel 15–19, key TS specs, ITU IMT-2020/2030, ETSI NFV/MEC, O-RAN WG1/4/6, media codecs, IEEE 802.11ax
- **48 technologies**: Full stack from mmWave to AV1 Codec
- **7 markets**: Enterprise 5G, Private 5G, Video Streaming, Open RAN, Edge Computing, etc.
- **16 products**: Ericsson Radio System, Nokia AirScale, Snapdragon X75, AWS Wavelength, and more
- **~400 relationships**: COMPETES_WITH pairs, MEMBER_OF links, SUPERSEDES chains, ENABLES/REQUIRES dependency graphs, SUPPLIES_TO chains, M&A events

---

## API Reference

| Endpoint | Description |
|---|---|
| `GET /api/graph/node/{id}` | Single node details |
| `GET /api/graph/neighbors/{id}?depth=1&types=` | Expand neighbors (up to depth 3) |
| `GET /api/graph/path?from_id=&to_id=` | Shortest path between two nodes |
| `GET /api/graph/subgraph?label=Company&limit=50` | All nodes of a type |
| `GET /api/taxonomy` | TMT technology hierarchy |
| `GET /api/search?q=&labels=` | Full-text entity search |
| `GET /api/intelligence/competitors/{company_id}` | Competitor analysis |
| `GET /api/intelligence/events?type=M&A&since=2023-01-01` | Event timeline |
| `GET /api/standards?body=3GPP&status=Frozen` | Standards list |
| `GET /api/standards/{id}/implementors` | Products implementing a standard |
| `POST /api/ingest/article` | Extract entities from pasted text |
| `POST /api/ingest/trigger` | Trigger RSS feed poll |
| `GET /api/ingest/status` | Ingestion pipeline status |
| `GET /health` | Health check |

---

## Ingestion Pipeline

### RSS Feeds (auto-polled every 4h)
Light Reading · Fierce Telecom · Fierce Wireless · RCR Wireless · SDxCentral · Telecom TV · 3GPP News · GSMA Newsroom · ITU News · O-RAN Alliance Blog · Telegeography · The Verge Tech · Ars Technica

### Extraction Flow
1. `feedparser` polls each feed, fetches latest 10 entries
2. `httpx` + `BeautifulSoup4` fetches full article text
3. Upstash Redis deduplicates by URL (SISMEMBER check)
4. Claude API (`claude-opus-4-5`) extracts entities + relationships via forced `tool_use`
5. `rapidfuzz` normalizes extracted names to canonical seed names (threshold: 90)
6. Neo4j `MERGE` writes entities and relationships (confidence ≥ 0.75 only)
7. `Article` node created only when ≥1 new relationship was written (preserves 200k node limit)

### Manual Extraction
`POST /api/ingest/article` with `{title, content, source}` — extracts and writes in one step. Returns extracted entities and relationships for preview.

---

## Deployment

### Railway (Backend)
1. Connect Railway to this GitHub repo
2. Set root directory to `backend/`
3. Add environment variables: `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`, `ANTHROPIC_API_KEY`
4. Deploy — `railway.toml` configures the start command automatically

### Vercel (Frontend)
1. Import this repo in Vercel
2. Set root directory to `frontend/`
3. Add environment variable: `NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app`
4. Deploy

### Neo4j Aura Free
1. Create a free instance at [console.neo4j.io](https://console.neo4j.io)
2. Copy the Bolt connection URI (starts with `neo4j+s://`)
3. Set `NEO4J_URI` and `NEO4J_PASSWORD` in your backend environment

---

## Key Design Decisions

**Why Neo4j over a relational DB?** The TMT domain is fundamentally about relationships — competitive dynamics, supply chains, standard dependencies. Cypher's pattern matching (`MATCH path = (a)-[*1..3]-(b)`) makes multi-hop traversals trivial.

**Why not Docker?** All services (Neo4j Aura, Upstash Redis) have free cloud tiers. Local dev points directly at cloud instances — no containers needed.

**Node limit management:** Neo4j Aura Free has a 200k node limit. `Article` nodes are only created when at least one new relationship was written, preventing node accumulation from high-volume feeds.

**Confidence threshold (0.75):** LLM extraction at lower confidence introduces entity fragmentation. The `rapidfuzz` normalization layer catches name variants within the 0.75–1.0 band; anything below is discarded.

---

## What Gets Updated With Each Run

After each RSS ingestion cycle, check `GET /api/ingest/status` for:
- `last_run`: ISO timestamp of last completed run
- `articles_processed`: cumulative count
- `queue_depth`: pending extractions in Redis
- `scheduler_running`: whether APScheduler is active

New entities/relationships appear in the graph immediately after writing. The frontend reads directly from Neo4j Aura on each page load — no separate cache TTL to worry about.
