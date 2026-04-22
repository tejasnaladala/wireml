import { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import * as icons from 'lucide-react';
import { getSchema } from '@wireml/nodes';
import clsx from 'clsx';

interface NodeData extends Record<string, unknown> {
  schemaId: string;
}

const CATEGORY_COLORS: Record<string, string> = {
  data: 'bg-wire-data/10 border-wire-data',
  preprocess: 'bg-wire-preprocess/10 border-wire-preprocess',
  backbone: 'bg-wire-backbone/10 border-wire-backbone',
  head: 'bg-wire-head/10 border-wire-head',
  eval: 'bg-wire-eval/10 border-wire-eval',
  deploy: 'bg-wire-deploy/10 border-wire-deploy',
};

const CATEGORY_TEXT: Record<string, string> = {
  data: 'text-wire-data',
  preprocess: 'text-wire-preprocess',
  backbone: 'text-wire-backbone',
  head: 'text-wire-head',
  eval: 'text-wire-eval',
  deploy: 'text-wire-deploy',
};

export const NodeView = memo(({ data, selected }: NodeProps) => {
  const schema = getSchema((data as NodeData).schemaId);
  const Icon = (schema.icon && (icons as any)[schema.icon]) || icons.Box;

  return (
    <div
      className={clsx(
        'rounded-xl border min-w-[200px] bg-wire-surface overflow-hidden',
        CATEGORY_COLORS[schema.category],
        selected ? 'shadow-node-selected' : 'shadow-node',
      )}
    >
      <div className={clsx('flex items-center gap-2 px-3 py-2 border-b border-wire-border')}>
        <Icon size={14} className={CATEGORY_TEXT[schema.category]} />
        <span className="text-xs uppercase tracking-wider font-semibold text-wire-muted">
          {schema.category}
        </span>
      </div>

      <div className="px-3 py-2.5">
        <div className="text-sm font-semibold text-wire-text">{schema.name}</div>
        <div className="text-[11px] text-wire-muted line-clamp-2 mt-0.5">
          {schema.description}
        </div>
      </div>

      <div className="px-3 py-2 border-t border-wire-border bg-wire-surface-2/40 flex items-center justify-between gap-2">
        <span className="text-[10px] uppercase text-wire-muted tracking-wide">
          {schema.executionMode === 'reactive' ? '◉ reactive' : '▶ triggered'}
        </span>
        {schema.capability.localOnly && (
          <span className="text-[10px] text-wire-head uppercase tracking-wide">Local only</span>
        )}
      </div>

      {schema.inputs.map((port, i) => (
        <Handle
          key={`in-${port.name}`}
          type="target"
          position={Position.Left}
          id={port.name}
          style={{ top: 60 + i * 22 }}
          title={`${port.name} (${port.type})`}
        />
      ))}
      {schema.outputs.map((port, i) => (
        <Handle
          key={`out-${port.name}`}
          type="source"
          position={Position.Right}
          id={port.name}
          style={{ top: 60 + i * 22 }}
          title={`${port.name} (${port.type})`}
        />
      ))}
    </div>
  );
});
NodeView.displayName = 'NodeView';
