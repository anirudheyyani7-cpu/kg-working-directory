"use client";
import { useEffect, useRef, useCallback, useState } from "react";
import { useGraphStore } from "@/store/graphStore";
import { NODE_COLORS, GraphNode, GraphLink } from "@/types/graph";
import { api } from "@/lib/api";
import NodeDetailPanel from "./NodeDetailPanel";
import GraphControls from "./GraphControls";

export default function ForceExplorer({ initialLabel = "Company" }: { initialLabel?: string }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const graphRef = useRef<any>(null);
  const [ForceGraph2D, setForceGraph2D] = useState<any>(null);
  const { graphData, visibleLabels, setSelectedNode, mergeGraphData, pushHistory } = useGraphStore();

  useEffect(() => {
    import("react-force-graph-2d").then((mod) => {
      setForceGraph2D(() => mod.default);
    });
  }, []);

  useEffect(() => {
    api.getSubgraph(initialLabel, 60).then((data: any) => mergeGraphData(data)).catch(() => {});
  }, [initialLabel, mergeGraphData]);

  const filteredData = {
    nodes: graphData.nodes.filter((n) => visibleLabels.has(n.label)),
    links: graphData.links,
  };

  const handleNodeClick = useCallback(async (node: GraphNode) => {
    setSelectedNode(node);
    pushHistory(node.id);
  }, [setSelectedNode, pushHistory]);

  const paintNode = useCallback((node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
    const label = node.label as string;
    const color = NODE_COLORS[label] || "#6b7280";
    const size = Math.max(4, (node.val || 6) / 2);
    ctx.beginPath();
    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();
    if (globalScale > 1.5) {
      ctx.font = `${Math.max(8, 12 / globalScale)}px sans-serif`;
      ctx.fillStyle = "#111";
      ctx.fillText(node.name.slice(0, 20), node.x + size + 2, node.y + 3);
    }
  }, []);

  if (typeof window === "undefined") {
    return <div className="w-full h-full bg-gray-50 dark:bg-gray-900 flex items-center justify-center text-gray-400">Loading graph...</div>;
  }

  if (!ForceGraph2D) {
    return (
      <div
        ref={containerRef}
        className="w-full h-full bg-gray-50 dark:bg-gray-900 flex items-center justify-center text-gray-400 relative"
      >
        <span>Loading graph engine...</span>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="w-full h-full relative overflow-hidden">
      <ForceGraph2D
        ref={graphRef}
        graphData={filteredData}
        nodeId="id"
        nodeLabel="name"
        linkSource="source"
        linkTarget="target"
        linkLabel="type"
        onNodeClick={handleNodeClick}
        nodeCanvasObject={paintNode}
        linkColor={() => "#e5e7eb"}
        linkWidth={1}
        backgroundColor="#f9fafb"
        width={containerRef.current?.clientWidth}
        height={containerRef.current?.clientHeight}
        cooldownTicks={100}
      />
      <NodeDetailPanel />
      <GraphControls />
    </div>
  );
}
