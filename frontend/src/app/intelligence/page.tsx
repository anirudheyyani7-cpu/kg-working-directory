import { api } from "@/lib/api";

interface Event {
  name: string;
  event_type: string;
  date: string;
  value_usd_bn?: number;
  status: string;
  description?: string;
  companies: string[];
}

const EVENT_COLORS: Record<string, string> = {
  "M&A": "bg-blue-100 text-blue-800",
  "Partnership": "bg-emerald-100 text-emerald-800",
  "Product Launch": "bg-violet-100 text-violet-800",
  "Standard Release": "bg-amber-100 text-amber-800",
};

export default async function IntelligencePage() {
  let allEvents: Event[] = [];
  let maEvents: Event[] = [];
  let partnerships: Event[] = [];

  try {
    [allEvents, maEvents, partnerships] = await Promise.all([
      api.getEvents() as Promise<Event[]>,
      api.getEvents("M&A") as Promise<Event[]>,
      api.getEvents("Partnership") as Promise<Event[]>,
    ]);
  } catch {}

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <a href="/" className="text-sm text-gray-400 hover:text-gray-600">← Home</a>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">Competitive Intelligence</h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {[
            { label: "Total Events", value: allEvents.length, color: "text-blue-600" },
            { label: "M&A Deals", value: maEvents.length, color: "text-violet-600" },
            { label: "Partnerships", value: partnerships.length, color: "text-emerald-600" },
          ].map((s) => (
            <div key={s.label} className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 p-5">
              <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
              <p className="text-sm text-gray-500 mt-1">{s.label}</p>
            </div>
          ))}
        </div>

        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-100 dark:border-gray-800">
            <h2 className="font-semibold text-gray-900 dark:text-white">Event Timeline</h2>
          </div>
          <div className="divide-y divide-gray-50 dark:divide-gray-800">
            {allEvents.length === 0 && (
              <p className="px-6 py-8 text-center text-gray-400 text-sm">No events found. Run seed data or ingest articles.</p>
            )}
            {allEvents.map((ev, i) => (
              <div key={i} className="px-6 py-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${EVENT_COLORS[ev.event_type] || "bg-gray-100 text-gray-700"}`}>
                        {ev.event_type}
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${ev.status === "Completed" ? "bg-green-100 text-green-700" : ev.status === "Active" ? "bg-blue-100 text-blue-700" : "bg-red-100 text-red-700"}`}>
                        {ev.status}
                      </span>
                    </div>
                    <h3 className="font-medium text-gray-900 dark:text-white">{ev.name}</h3>
                    {ev.description && <p className="text-sm text-gray-500 mt-1 line-clamp-2">{ev.description}</p>}
                    {ev.companies?.length > 0 && (
                      <div className="flex gap-1 mt-2 flex-wrap">
                        {ev.companies.map((c) => (
                          <span key={c} className="text-xs bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 px-2 py-0.5 rounded">{c}</span>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="text-right shrink-0">
                    {ev.date && <p className="text-xs text-gray-400">{ev.date}</p>}
                    {ev.value_usd_bn && <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">${ev.value_usd_bn}B</p>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
