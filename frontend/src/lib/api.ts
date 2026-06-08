const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}/api${path}`);
  if (!res.ok) throw new Error(`API error ${res.status}: ${path}`);
  return res.json();
}

export const api = {
  getNode: (id: string) => apiFetch<Record<string, unknown>>(`/graph/node/${encodeURIComponent(id)}`),
  getNeighbors: (id: string, depth = 1, types?: string) =>
    apiFetch(`/graph/neighbors/${encodeURIComponent(id)}?depth=${depth}${types ? `&types=${types}` : ""}`),
  getSubgraph: (label: string, limit = 50) => apiFetch(`/graph/subgraph?label=${label}&limit=${limit}`),
  getPath: (fromId: string, toId: string) => apiFetch(`/graph/path?from_id=${fromId}&to_id=${toId}`),
  search: (q: string, labels?: string) =>
    apiFetch(`/search/?q=${encodeURIComponent(q)}${labels ? `&labels=${labels}` : ""}`),
  getTaxonomy: () => apiFetch("/taxonomy/"),
  getCompetitors: (companyId: string) => apiFetch(`/intelligence/competitors/${encodeURIComponent(companyId)}`),
  getEvents: (type?: string, since?: string) =>
    apiFetch(`/intelligence/events${type ? `?type=${type}` : ""}${since ? `${type ? "&" : "?"}since=${since}` : ""}`),
  getStandards: (body?: string, status?: string) =>
    apiFetch(`/standards/${body ? `?body=${body}` : ""}${status ? `${body ? "&" : "?"}status=${status}` : ""}`),
  getStandardImplementors: (id: string) => apiFetch(`/standards/${encodeURIComponent(id)}/implementors`),
  ingestArticle: (data: { title: string; content: string; source?: string; url?: string }) =>
    fetch(`${BASE_URL}/api/ingest/article`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }).then((r) => r.json()),
  triggerIngest: () =>
    fetch(`${BASE_URL}/api/ingest/trigger`, { method: "POST" }).then((r) => r.json()),
  getIngestStatus: () => apiFetch("/ingest/status"),
};
