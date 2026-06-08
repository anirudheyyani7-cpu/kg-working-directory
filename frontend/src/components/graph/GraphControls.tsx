"use client";
import { useGraphStore } from "@/store/graphStore";
import { NODE_COLORS } from "@/types/graph";

const LABELS = ["Company", "Technology", "Standard", "Product", "RegBody", "Market", "Event"];

export default function GraphControls() {
  const { visibleLabels, toggleLabel, resetGraph } = useGraphStore();
  return (
    <div className="absolute bottom-4 left-4 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl shadow-lg px-4 py-3 z-10 flex flex-col gap-2">
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs font-semibold text-gray-500 uppercase tracking-wide">Filter nodes</span>
        <button onClick={resetGraph} className="text-xs text-red-500 hover:text-red-700 font-medium ml-4">Reset</button>
      </div>
      <div className="flex flex-wrap gap-1.5">
        {LABELS.map((label) => {
          const active = visibleLabels.has(label);
          const color = NODE_COLORS[label];
          return (
            <button
              key={label}
              onClick={() => toggleLabel(label)}
              className={`text-xs px-2 py-1 rounded-full font-medium border transition-all ${
                active ? "text-white border-transparent" : "bg-white dark:bg-gray-800 text-gray-500 border-gray-200"
              }`}
              style={active ? { backgroundColor: color, borderColor: color } : {}}
            >
              {label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
