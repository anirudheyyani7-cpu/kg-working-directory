import { api } from "@/lib/api";

interface Standard {
  name: string;
  identifier: string;
  issuing_body: string;
  status: string;
  published_date: string;
  description: string;
}

const STATUS_COLORS: Record<string, string> = {
  Frozen: "bg-blue-100 text-blue-800",
  Stable: "bg-green-100 text-green-800",
  Draft: "bg-yellow-100 text-yellow-800",
  Withdrawn: "bg-red-100 text-red-700",
};

export default async function StandardsPage() {
  let standards: Standard[] = [];
  try {
    standards = await api.getStandards() as Standard[];
  } catch {}

  const bodies = [...new Set(standards.map((s) => s.issuing_body))].filter(Boolean);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <a href="/" className="text-sm text-gray-400 hover:text-gray-600">← Home</a>
          <h1 className="text-xl font-bold text-gray-900 dark:text-white">Standards Tracker</h1>
          <span className="text-sm text-gray-400">{standards.length} standards from {bodies.length} bodies</span>
        </div>

        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 dark:bg-gray-800 text-gray-500 uppercase text-xs tracking-wide">
              <tr>
                <th className="px-4 py-3 text-left">Standard</th>
                <th className="px-4 py-3 text-left">Body</th>
                <th className="px-4 py-3 text-left">Status</th>
                <th className="px-4 py-3 text-left">Published</th>
                <th className="px-4 py-3 text-left">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {standards.length === 0 && (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400">No standards found. Run seed data.</td></tr>
              )}
              {standards.map((s, i) => (
                <tr key={i} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-900 dark:text-white">{s.name}</div>
                    {s.identifier && s.identifier !== s.name && (
                      <div className="text-xs text-gray-400">{s.identifier}</div>
                    )}
                  </td>
                  <td className="px-4 py-3 text-gray-600 dark:text-gray-400">{s.issuing_body}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${STATUS_COLORS[s.status] || "bg-gray-100 text-gray-700"}`}>
                      {s.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500 whitespace-nowrap">{s.published_date?.slice(0, 10)}</td>
                  <td className="px-4 py-3 text-gray-500 max-w-xs truncate">{s.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
