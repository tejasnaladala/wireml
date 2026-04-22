import { useMemo } from 'react';
import { getSchema } from '@wireml/nodes';
import { useGraphStore } from '@/store/graphStore';

export function Inspector() {
  const selectedNodeId = useGraphStore((s) => s.selectedNodeId);
  const graph = useGraphStore((s) => s.graph);
  const updateNodeParams = useGraphStore((s) => s.updateNodeParams);

  const node = useMemo(
    () => graph.nodes.find((n) => n.id === selectedNodeId),
    [graph.nodes, selectedNodeId],
  );

  if (!node) {
    return (
      <aside className="w-[300px] bg-wire-surface border-l border-wire-border p-4 text-sm text-wire-muted">
        <p>Select a node to configure.</p>
      </aside>
    );
  }

  const schema = getSchema(node.schemaId);

  return (
    <aside className="w-[300px] bg-wire-surface border-l border-wire-border flex flex-col overflow-hidden">
      <div className="p-4 border-b border-wire-border">
        <div className="text-[10px] uppercase tracking-wider text-wire-muted">
          {schema.category}
        </div>
        <div className="text-base font-semibold mt-0.5">{schema.name}</div>
        <div className="text-xs text-wire-muted mt-1.5 leading-relaxed">{schema.description}</div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {schema.params.length === 0 && (
          <p className="text-xs text-wire-muted">No parameters.</p>
        )}
        {schema.params.map((p) => {
          const current = node.params[p.name] ?? p.default;
          return (
            <div key={p.name} className="mb-3">
              <label className="text-xs uppercase tracking-wide text-wire-muted block mb-1">
                {p.label ?? p.name}
              </label>
              {p.kind === 'number' && (
                <input
                  type="number"
                  value={String(current ?? '')}
                  min={p.min}
                  max={p.max}
                  step={p.step ?? 1}
                  onChange={(e) => updateNodeParams(node.id, { [p.name]: Number(e.target.value) })}
                  className="w-full px-2 py-1.5 text-sm bg-wire-surface-2 border border-wire-border rounded-md focus:outline-none focus:border-wire-accent"
                />
              )}
              {p.kind === 'string' && (
                <input
                  type="text"
                  value={String(current ?? '')}
                  onChange={(e) => updateNodeParams(node.id, { [p.name]: e.target.value })}
                  className="w-full px-2 py-1.5 text-sm bg-wire-surface-2 border border-wire-border rounded-md focus:outline-none focus:border-wire-accent"
                />
              )}
              {p.kind === 'enum' && (
                <select
                  value={String(current ?? '')}
                  onChange={(e) => updateNodeParams(node.id, { [p.name]: e.target.value })}
                  className="w-full px-2 py-1.5 text-sm bg-wire-surface-2 border border-wire-border rounded-md focus:outline-none focus:border-wire-accent"
                >
                  {p.options?.map((o) => (
                    <option key={o} value={o}>
                      {o}
                    </option>
                  ))}
                </select>
              )}
              {p.kind === 'boolean' && (
                <label className="inline-flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={Boolean(current)}
                    onChange={(e) => updateNodeParams(node.id, { [p.name]: e.target.checked })}
                    className="accent-wire-accent"
                  />
                  <span>{Boolean(current) ? 'On' : 'Off'}</span>
                </label>
              )}
              {p.kind === 'json' && (
                <textarea
                  value={JSON.stringify(current ?? null, null, 2)}
                  onChange={(e) => {
                    try {
                      const v = JSON.parse(e.target.value);
                      updateNodeParams(node.id, { [p.name]: v });
                    } catch {
                      /* swallow parse errors while typing */
                    }
                  }}
                  rows={5}
                  className="w-full px-2 py-1.5 text-xs font-mono bg-wire-surface-2 border border-wire-border rounded-md focus:outline-none focus:border-wire-accent"
                />
              )}
              {p.description && (
                <p className="text-[10px] text-wire-muted mt-1">{p.description}</p>
              )}
            </div>
          );
        })}
      </div>
    </aside>
  );
}
