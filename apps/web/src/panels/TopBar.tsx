import * as icons from 'lucide-react';
import { useRuntimeStore } from '@/store/runtimeStore';
import { useGraphStore } from '@/store/graphStore';
import clsx from 'clsx';

interface TopBarProps {
  onOpenTemplates: () => void;
  onRun: () => void;
  running: boolean;
}

export function TopBar({ onOpenTemplates, onRun, running }: TopBarProps) {
  const kind = useRuntimeStore((s) => s.kind);
  const local = useRuntimeStore((s) => s.local);
  const web = useRuntimeStore((s) => s.web);
  const setKind = useRuntimeStore((s) => s.setKind);
  const graph = useGraphStore((s) => s.graph);

  const currentCaps = kind === 'local' ? local : web;
  const canGoLocal = local != null;

  return (
    <header className="h-12 flex items-center gap-3 px-4 bg-wire-surface border-b border-wire-border">
      <div className="flex items-center gap-2">
        <div className="w-6 h-6 rounded-md bg-gradient-to-br from-wire-accent to-wire-backbone" />
        <span className="text-sm font-semibold tracking-tight">WireML</span>
      </div>

      <div className="h-4 w-px bg-wire-border" />

      <div className="text-sm text-wire-muted truncate max-w-[240px]">{graph.name}</div>

      <button onClick={onOpenTemplates} className="btn-ghost ml-2">
        <icons.Layers size={14} />
        Templates
      </button>

      <div className="flex-1" />

      <div
        className={clsx(
          'flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-full border',
          kind === 'local'
            ? 'bg-wire-head/10 border-wire-head text-wire-head'
            : 'bg-wire-backbone/10 border-wire-backbone text-wire-backbone',
        )}
        title={currentCaps ? `${currentCaps.device.type} — ${currentCaps.device.name}` : undefined}
      >
        <icons.Cpu size={12} />
        <span className="uppercase tracking-wide font-medium">
          {kind === 'local' ? 'Power mode' : 'Web mode'}
        </span>
        {currentCaps && <span className="text-wire-muted">· {currentCaps.device.type}</span>}
      </div>

      <button
        disabled={!canGoLocal}
        onClick={() => setKind(kind === 'local' ? 'web' : 'local')}
        className={clsx(
          'btn-ghost',
          !canGoLocal && 'cursor-not-allowed opacity-40',
        )}
        title={
          canGoLocal
            ? `Toggle runtime (${local?.device.name})`
            : 'No local runtime detected. Run `docker compose up` or `pnpm dev:runtime` to enable.'
        }
      >
        <icons.ArrowLeftRight size={14} />
        Toggle
      </button>

      <button onClick={onRun} disabled={running} className="btn-primary">
        {running ? (
          <>
            <icons.LoaderCircle size={14} className="animate-spin" /> Running…
          </>
        ) : (
          <>
            <icons.Play size={14} /> Run graph
          </>
        )}
      </button>
    </header>
  );
}
