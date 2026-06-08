"use client";
import { useEffect, useRef } from "react";
import type { TaxonomyData } from "@/app/taxonomy/page";

interface Props { data: TaxonomyData }

export default function TaxonomyTree({ data }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !data) return;

    Promise.all([
      import("cytoscape"),
      import("cytoscape-dagre"),
    ]).then(([cyModule, dagreModule]) => {
      const cytoscape = cyModule.default;
      const dagre = dagreModule.default;
      cytoscape.use(dagre);

      const nodes: any[] = [];
      const edges: any[] = [];
      const colors: Record<string, string> = {
        RAN: "#3b82f6", Core: "#10b981", Edge: "#06b6d4", AI_ML: "#f59e0b",
        Transport: "#8b5cf6", Media: "#ec4899", Other: "#6b7280",
      };

      Object.entries(data.categories || {}).forEach(([cat, techs]) => {
        nodes.push({ data: { id: `cat_${cat}`, label: cat, type: "category" }, classes: "category" });
        (techs as any[]).forEach((t) => {
          const tId = `tech_${t.name.replace(/\s+/g, "_")}`;
          if (!nodes.find((n) => n.data.id === tId)) {
            nodes.push({ data: { id: tId, label: t.name, type: "tech" }, classes: "tech" });
          }
          edges.push({ data: { source: `cat_${cat}`, target: tId } });
          (t.enables || []).forEach((subTech: string) => {
            const subId = `tech_${subTech.replace(/\s+/g, "_")}`;
            edges.push({ data: { source: tId, target: subId } });
          });
        });
      });

      const cy = cytoscape({
        container: containerRef.current!,
        elements: { nodes, edges },
        style: [
          { selector: "node.category", style: { "background-color": "#1e293b", "label": "data(label)", "color": "#fff", "font-size": 11, "text-valign": "center", "text-halign": "center", width: 120, height: 30, shape: "round-rectangle" } },
          { selector: "node.tech", style: { "background-color": "#3b82f6", "label": "data(label)", "color": "#fff", "font-size": 9, "text-valign": "center", "text-halign": "center", width: 100, height: 24, shape: "round-rectangle" } },
          { selector: "edge", style: { "line-color": "#e2e8f0", "target-arrow-color": "#e2e8f0", "target-arrow-shape": "triangle", "curve-style": "bezier", width: 1.5 } },
        ],
        layout: { name: "dagre", rankDir: "LR", nodeSep: 30, rankSep: 80 } as any,
      });

      return () => cy.destroy();
    });
  }, [data]);

  return <div ref={containerRef} className="w-full h-full" />;
}
