"use client";
import { useGraphStore } from "@/store/graphStore";
import { NODE_COLORS } from "@/types/graph";
import { api } from "@/lib/api";

export default function NodeDetailPanel() {
  const { selectedNode, setSelectedNode, mergeGraphData } = useGraphStore();
  if (!selectedNode) return null;

  const color = NODE_COLORS[selectedNode.label] || "#6b7280";

  const handleExpand = async () => {
    try {
      const data = await api.getNeighbors(selectedNode.id, 1) as { nodes: unknown[]; links: unknown[] };
      mergeGraphData(data as any);
    } catch {}
  };

  return (
    <div className="absolute top-4 right-4 w-72 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl z-10 overflow-hidden">
      <div className="px-4 py-3 flex items-center justify-between" style={{ backgroundColor: color + "22", borderBottom: `2px solid ${color}` }}>
        <div>
          <span className="text-xs font-semibold uppercase tracking-wide" style={{ color }}>{selectedNode.label}</span>
          <h3 className="font-bold text-gray-900 dark:text-white text-sm mt-0.5">{selectedNode.name}</h3>
        </div>
        <button onClick={() => setSelectedNode(null)} className="text-gray-400 hover:text-gray-600 text-lg leading-none">×</button>
      </div>
      <div className="px-4 py-3 max-h-64 overflow-y-auto">
        {selectedNode.properties && Object.entries(selectedNode.properties)
          .filter(([k]) => !["id", "name"].includes(k) && k !== "source_urls")
          .slice(0, 12)
          .map(([k, v]) => (
            <div key={k} className="flex justify-between text-xs py-1 border-b border-gray-100 dark:border-gray-800">
              <span className="text-gray-500 capitalize">{k.replace(/_/g, " ")}</span>
              <span className="text-gray-900 dark:text-white font-medium ml-2 text-right max-w-[60%] truncate">
                {String(v)}
              </span>
            </div>
          ))}
      </div>
      <div className="px-4 py-3 flex gap-2">
        <button onClick={handleExpand} className="flex-1 text-xs py-1.5 rounded bg-blue-50 text-blue-700 hover:bg-blue-100 font-medium transition-colors">
          Expand neighbors
        </button>
      </div>
    </div>
  );
}
