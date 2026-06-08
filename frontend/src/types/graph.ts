export interface GraphNode {
  id: string;
  label: string;
  name: string;
  group?: number;
  val?: number;
  properties?: Record<string, unknown>;
  // react-force-graph internal
  x?: number;
  y?: number;
  fx?: number;
  fy?: number;
}

export interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  type: string;
  properties?: Record<string, unknown>;
}

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

export const NODE_COLORS: Record<string, string> = {
  Company: "#3b82f6",       // blue
  Technology: "#10b981",    // emerald
  Standard: "#f59e0b",      // amber
  Product: "#8b5cf6",       // violet
  RegBody: "#ef4444",       // red
  Market: "#06b6d4",        // cyan
  Person: "#f97316",        // orange
  Event: "#ec4899",         // pink
  Article: "#6b7280",       // gray
};

export const NODE_GROUPS: Record<string, number> = {
  Company: 1,
  Technology: 2,
  Standard: 3,
  Product: 4,
  RegBody: 5,
  Market: 6,
  Person: 7,
  Event: 8,
};
