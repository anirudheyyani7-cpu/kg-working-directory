"use client";
import { useState } from "react";
import { api } from "@/lib/api";

interface ExtractionResult {
  entities_extracted: number;
  relationships_extracted: number;
  new_relationships_written: number;
  entities: { type: string; name: string; confidence: number }[];
  relationships: { source: string; type: string; target: string; confidence: number }[];
}

export default function IngestPage() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [source, setSource] = useState("manual");
  const [result, setResult] = useState<ExtractionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [triggerMsg, setTriggerMsg] = useState("");

  const handleExtract = async () => {
    if (!content.trim()) return;
    setLoading(true);
    setError("");
    try {
      const data = await api.ingestArticle({ title, content, source });
      setResult(data);
    } catch (e: any) {
      setError(e.message || "Extraction failed");
    } finally {
      setLoading(false);
    }
  };

  const handleTrigger = async () => {
    try {
      const data = await api.triggerIngest();
      setTriggerMsg(data.message || "Triggered");
    } catch (e: any) {
      setTriggerMsg("Error: " + e.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-6">
      <div className="max-w-3xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <a href="/" className="text-sm text-gray-400 hover:text-gray-600">← Home</a>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">Ingest Data</h1>
        </div>

        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 mb-6">
          <h2 className="font-semibold text-gray-900 dark:text-white mb-4">Paste Article for LLM Extraction</h2>
          <input
            className="w-full border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm mb-3 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            placeholder="Article title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <input
            className="w-full border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm mb-3 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
            placeholder="Source (e.g. Light Reading)"
            value={source}
            onChange={(e) => setSource(e.target.value)}
          />
          <textarea
            className="w-full border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm mb-3 bg-white dark:bg-gray-800 text-gray-900 dark:text-white resize-none"
            rows={8}
            placeholder="Paste article text here..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
          {error && <p className="text-red-500 text-sm mb-3">{error}</p>}
          <button
            onClick={handleExtract}
            disabled={loading || !content.trim()}
            className="w-full py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
          >
            {loading ? "Extracting with Claude..." : "Extract & Write to Graph"}
          </button>
        </div>

        {result && (
          <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6 mb-6">
            <h2 className="font-semibold text-gray-900 dark:text-white mb-3">Extraction Results</h2>
            <div className="grid grid-cols-3 gap-3 mb-4">
              {[
                { label: "Entities", value: result.entities_extracted },
                { label: "Relationships", value: result.relationships_extracted },
                { label: "Written to Graph", value: result.new_relationships_written, highlight: true },
              ].map((s) => (
                <div key={s.label} className={`rounded-lg p-3 text-center ${s.highlight ? "bg-green-50 border border-green-200" : "bg-gray-50 dark:bg-gray-800"}`}>
                  <p className={`text-xl font-bold ${s.highlight ? "text-green-600" : "text-gray-900 dark:text-white"}`}>{s.value}</p>
                  <p className="text-xs text-gray-500">{s.label}</p>
                </div>
              ))}
            </div>
            <div className="space-y-4">
              {result.entities.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Entities extracted</h3>
                  <div className="flex flex-wrap gap-1.5">
                    {result.entities.map((e, i) => (
                      <span key={i} className="text-xs bg-blue-50 text-blue-700 border border-blue-200 px-2 py-0.5 rounded-full">
                        {e.type}: {e.name} ({(e.confidence * 100).toFixed(0)}%)
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {result.relationships.length > 0 && (
                <div>
                  <h3 className="text-xs font-semibold text-gray-500 uppercase mb-2">Relationships extracted</h3>
                  <div className="space-y-1">
                    {result.relationships.map((r, i) => (
                      <div key={i} className="text-xs text-gray-600 dark:text-gray-400 flex items-center gap-1">
                        <span className="font-medium text-gray-800 dark:text-gray-200">{r.source}</span>
                        <span className="text-blue-500">→[{r.type}]→</span>
                        <span className="font-medium text-gray-800 dark:text-gray-200">{r.target}</span>
                        <span className="text-gray-400 ml-auto">({(r.confidence * 100).toFixed(0)}%)</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-6">
          <h2 className="font-semibold text-gray-900 dark:text-white mb-2">RSS Feed Ingestion</h2>
          <p className="text-sm text-gray-500 mb-4">Trigger a manual poll of all 13 RSS feeds. The scheduler runs automatically every 4 hours.</p>
          <button onClick={handleTrigger} className="py-2 px-4 rounded-lg bg-emerald-600 text-white font-medium hover:bg-emerald-700 transition-colors text-sm">
            Trigger RSS Poll Now
          </button>
          {triggerMsg && <p className="text-sm text-gray-600 dark:text-gray-400 mt-3">{triggerMsg}</p>}
        </div>
      </div>
    </div>
  );
}
