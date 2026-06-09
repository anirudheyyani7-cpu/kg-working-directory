import { api } from "@/lib/api";
import TaxonomyTree from "@/components/graph/TaxonomyTree";

export interface TaxonomyData {
  categories: Record<string, { name: string; generation?: string; enables: string[] }[]>;
}

export default async function TaxonomyPage() {
  let data: TaxonomyData = { categories: {} };
  try {
    data = await api.getTaxonomy() as TaxonomyData;
  } catch {}

  const categoryCount = Object.keys(data.categories).length;

  return (
    <div className="flex flex-col h-screen">
      <div className="px-6 py-3 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800 flex items-center gap-4">
        <a href="/" className="text-sm text-gray-400 hover:text-gray-600">← Home</a>
        <h1 className="text-base font-semibold text-gray-900 dark:text-white">Domain Taxonomy</h1>
        <span className="text-xs text-gray-400">{categoryCount} categories · hierarchical view of TMT technologies</span>
      </div>
      <div className="flex-1 relative bg-gray-50 dark:bg-gray-950">
        <TaxonomyTree data={data} />
      </div>
    </div>
  );
}
