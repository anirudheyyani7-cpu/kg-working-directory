"use client";
import dynamic from "next/dynamic";

const ForceExplorer = dynamic(() => import("@/components/graph/ForceExplorer"), { ssr: false, loading: () => <div className="flex items-center justify-center h-full text-gray-400">Loading graph...</div> });

export default function ExplorePage() {
  return (
    <div className="flex flex-col h-screen">
      <div className="px-6 py-3 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 flex items-center gap-4">
        <a href="/" className="text-sm text-gray-400 hover:text-gray-600">← Home</a>
        <h1 className="text-base font-semibold text-gray-900 dark:text-white">Relationship Explorer</h1>
        <span className="text-xs text-gray-400">Click a node to see details · Click "Expand neighbors" to grow the graph</span>
      </div>
      <div className="flex-1 relative">
        <ForceExplorer initialLabel="Company" />
      </div>
    </div>
  );
}
