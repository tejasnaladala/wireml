import { useMemo, useState } from 'react';
import * as icons from 'lucide-react';
import { NODE_SCHEMAS, type NodeSchema } from '@wireml/nodes';
import { useRuntimeStore } from '@/store/runtimeStore';
import { useGraphStore } from '@/store/graphStore';
import clsx from 'clsx';

const CATEGORY_ORDER: NodeSchema['category'][] = [
  'data',
  'preprocess',
  'backbone',
  'head',
  'eval',
  'deploy',
];

const CATEGORY_LABELS: Record<string, string> = {
  data: 'Data sources',
  preprocess: 'Preprocess',
  backbone: 'Backbones',
  head: 'Heads',
  eval: 'Evaluation',
  deploy: 'Deploy',
};

export function NodeLibrary() {
  const [query, setQuery] = useState('');
  const localRuntime = useRuntimeStore((s) => s.local);
  const addNode = useGraphStore((s) => s.addNode);

  const filtered = useMemo(() => {
    const q = query.toLowerCase().trim();
    return NODE_SCHEMAS.filter((s) => {
      if (!q) return true;
      return (
        s.id.includes(q) ||
        s.name.toLowerCase().includes(q) ||
        s.description.toLowerCase().includes(q)
      );
    });
  }, [query]);

  const grouped = useMemo(() => {
    const m = new Map<string, NodeSchema[]>();
    for (const s of filtered) {
      if (!m.has(s.category)) m.set(s.category, []);
      m.get(s.category)!.push(s);
    }
    return m;
  }, [filtered]);

  const handleAdd = (schemaId: string) => {
    addNode(schemaId, { x: 200 + Math.random() * 60, y: 200 + Math.random() * 60 });
  };

  return (
    <aside className="w-[272px] bg-wire-surface border-r border-wire-border flex flex-col">
      <div className="p-3 border-b border-wire-border">
        <h2 className="text-xs uppercase tracking-wider text-wire-muted mb-2">Node library</h2>
        <div className="relative">
          <icons.Search
            size={14}
            className="absolute left-2.5 top-1/2 -translate-y-1/2 text-wire-muted"
          />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search nodes..."
            className="w-full pl-8 pr-2 py-1.5 text-sm bg-wire-surface-2 border border-wire-border rounded-md placeholder:text-wire-muted focus:outline-none focus:border-wire-accent"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto px-2 py-2">
        {CATEGORY_ORDER.map((cat) => {
          const items = grouped.get(cat);
          if (!items?.length) return null;
          return (
            <section key={cat} className="mb-4">
              <div className="flex items-center gap-2 px-2 py-1">
                <span className={clsx('category-dot', cat)} />
                <h3 className="text-[11px] uppercase tracking-wider text-wire-muted font-semibold">
                  {CATEGORY_LABELS[cat]}
                </h3>
                <span className="text-[10px] text-wire-muted ml-auto">{items.length}</span>
              </div>
              <ul>
                {items.map((s) => {
                  const disabled = s.capability.localOnly && !localRuntime;
                  const Icon = (s.icon && (icons as any)[s.icon]) || icons.Box;
                  return (
                    <li key={s.id}>
                      <button
                        disabled={disabled}
                        onClick={() => handleAdd(s.id)}
                        className={clsx(
                          'w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-left text-sm transition-colors',
                          disabled
                            ? 'text-wire-muted cursor-not-allowed'
                            : 'hover:bg-wire-surface-2 text-wire-text',
                        )}
                        title={disabled ? 'Requires local Power Mode runtime' : s.description}
                      >
                        <Icon size={14} className="text-wire-muted flex-shrink-0" />
                        <span className="truncate">{s.name}</span>
                        {disabled && (
                          <icons.Lock size={11} className="text-wire-muted ml-auto flex-shrink-0" />
                        )}
                      </button>
                    </li>
                  );
                })}
              </ul>
            </section>
          );
        })}
      </div>
    </aside>
  );
}
