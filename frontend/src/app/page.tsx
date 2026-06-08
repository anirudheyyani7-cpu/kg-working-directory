import Link from "next/link";
import { api } from "@/lib/api";

async function getStats() {
  try {
    const [events, standards] = await Promise.all([
      api.getEvents(undefined, "2024-01-01") as Promise<any[]>,
      api.getStandards("3GPP", "Frozen") as Promise<any[]>,
    ]);
    return { recentEvents: events.slice(0, 5), frozenStandards: standards.length };
  } catch {
    return { recentEvents: [], frozenStandards: 0 };
  }
}

const TILES = [
  { href: "/explore", title: "Relationship Explorer", desc: "Navigate connections between companies, technologies, and standards in an interactive force-directed graph.", icon: "🔗", color: "blue" },
  { href: "/taxonomy", title: "Domain Taxonomy", desc: "Browse the hierarchical classification of TMT sub-domains from 5G RAN to media codecs.", icon: "🌲", color: "emerald" },
  { href: "/intelligence", title: "Competitive Intelligence", desc: "Track M&A activity, partnerships, and competitive positions across the TMT landscape.", icon: "📊", color: "violet" },
  { href: "/standards", title: "Standards Tracker", desc: "Map 3GPP, ITU, ETSI, and O-RAN specs to vendors and products implementing them.", icon: "📋", color: "amber" },
  { href: "/ingest", title: "Ingest Data", desc: "Paste articles or trigger RSS ingestion to automatically extract and add entities to the graph.", icon: "⚡", color: "pink" },
];

export default async function Home() {
  const { recentEvents, frozenStandards } = await getStats();

  return (
    <main className="min-h-screen bg-gray-50 dark:bg-gray-950 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">TMT Knowledge Graph</h1>
          <p className="text-gray-500 mt-2">Telecom, Media & Technology — connected intelligence</p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-10">
          {[
            { label: "Frozen 3GPP Standards", value: frozenStandards },
            { label: "Recent Events (2024)", value: recentEvents.length },
            { label: "Data Sources", value: "13 RSS feeds" },
          ].map((s) => (
            <div key={s.label} className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5">
              <p className="text-2xl font-bold text-gray-900 dark:text-white">{s.value}</p>
              <p className="text-sm text-gray-500 mt-1">{s.label}</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5 mb-10">
          {TILES.map((t) => (
            <Link key={t.href} href={t.href}
              className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 hover:shadow-md hover:border-blue-300 transition-all group">
              <span className="text-2xl">{t.icon}</span>
              <h2 className="font-semibold text-gray-900 dark:text-white mt-2 group-hover:text-blue-600 transition-colors">{t.title}</h2>
              <p className="text-sm text-gray-500 mt-1 leading-relaxed">{t.desc}</p>
            </Link>
          ))}
        </div>

        {recentEvents.length > 0 && (
          <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6">
            <h2 className="font-semibold text-gray-900 dark:text-white mb-4">Recent Events</h2>
            <div className="space-y-3">
              {recentEvents.map((ev: any, i: number) => (
                <div key={i} className="flex items-start gap-3">
                  <span className="text-xs bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 px-2 py-0.5 rounded-full font-medium mt-0.5">{ev.event_type}</span>
                  <div>
                    <p className="text-sm font-medium text-gray-800 dark:text-gray-200">{ev.name}</p>
                    <p className="text-xs text-gray-400">{ev.date}{ev.value_usd_bn ? ` · $${ev.value_usd_bn}B` : ""}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}
