import { create } from "zustand";
import { GraphData, GraphNode, GraphLink } from "@/types/graph";

interface GraphStore {
  graphData: GraphData;
  selectedNode: GraphNode | null;
  visibleLabels: Set<string>;
  history: string[];
  setSelectedNode: (node: GraphNode | null) => void;
  mergeGraphData: (newData: GraphData) => void;
  toggleLabel: (label: string) => void;
  resetGraph: () => void;
  pushHistory: (nodeId: string) => void;
}

const ALL_LABELS = new Set(["Company", "Technology", "Standard", "Product", "RegBody", "Market", "Event"]);

export const useGraphStore = create<GraphStore>((set) => ({
  graphData: { nodes: [], links: [] },
  selectedNode: null,
  visibleLabels: ALL_LABELS,
  history: [],
  setSelectedNode: (node) => set({ selectedNode: node }),
  mergeGraphData: (newData) =>
    set((state) => {
      const existingIds = new Set(state.graphData.nodes.map((n) => n.id));
      const newNodes = newData.nodes.filter((n) => !existingIds.has(n.id));
      return {
        graphData: {
          nodes: [...state.graphData.nodes, ...newNodes],
          links: [...state.graphData.links, ...newData.links],
        },
      };
    }),
  toggleLabel: (label) =>
    set((state) => {
      const next = new Set(state.visibleLabels);
      next.has(label) ? next.delete(label) : next.add(label);
      return { visibleLabels: next };
    }),
  resetGraph: () => set({ graphData: { nodes: [], links: [] }, selectedNode: null, history: [] }),
  pushHistory: (nodeId) => set((s) => ({ history: [...s.history.slice(-19), nodeId] })),
}));
