import { useEffect, useState, useCallback } from 'react';
import { Canvas } from '@/canvas/Canvas';
import { NodeLibrary } from '@/panels/NodeLibrary';
import { Inspector } from '@/panels/Inspector';
import { TemplateGallery } from '@/panels/TemplateGallery';
import { TopBar } from '@/panels/TopBar';
import { useGraphStore } from '@/store/graphStore';
import { useRuntimeStore, probeLocalRuntime, probeWebRuntime } from '@/store/runtimeStore';
import { WebGraphRunner } from '@/runtime/WebGraphRunner';
import { LocalGraphRunner } from '@/runtime/LocalGraphRunner';
import { runGraph, type NodeResultEntry } from '@/runtime/scheduler';
import { TEMPLATES } from '@wireml/templates';

export default function App() {
  const [galleryOpen, setGalleryOpen] = useState(true);
  const [running, setRunning] = useState(false);
  const [runLog, setRunLog] = useState<NodeResultEntry[]>([]);

  const setGraph = useGraphStore((s) => s.setGraph);
  const graph = useGraphStore((s) => s.graph);
  const runtimeKind = useRuntimeStore((s) => s.kind);
  const setLocal = useRuntimeStore((s) => s.setLocal);
  const setWeb = useRuntimeStore((s) => s.setWeb);
  const setProbing = useRuntimeStore((s) => s.setProbing);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setProbing(true);
      const [web, local] = await Promise.all([probeWebRuntime(), probeLocalRuntime()]);
      if (cancelled) return;
      setWeb(web);
      setLocal(local);
      setProbing(false);
    })();
    return () => {
      cancelled = true;
    };
  }, [setLocal, setWeb, setProbing]);

  // Default-load the image-classifier template on first mount.
  useEffect(() => {
    if (graph.nodes.length === 0 && TEMPLATES.length > 0) {
      setGraph(TEMPLATES[0]!.graph);
    }
  }, [graph.nodes.length, setGraph]);

  const onRun = useCallback(async () => {
    setRunning(true);
    setRunLog([]);
    const runner = runtimeKind === 'local' ? new LocalGraphRunner() : new WebGraphRunner();
    try {
      for await (const entry of runGraph(graph, runner)) {
        setRunLog((prev) => [...prev, entry]);
      }
    } finally {
      setRunning(false);
    }
  }, [graph, runtimeKind]);

  return (
    <div className="h-screen w-screen flex flex-col">
      <TopBar onOpenTemplates={() => setGalleryOpen(true)} onRun={onRun} running={running} />
      <div className="flex-1 flex overflow-hidden">
        <NodeLibrary />
        <main className="flex-1 relative">
          <Canvas />
          {runLog.length > 0 && (
            <div className="absolute bottom-4 left-4 max-w-sm bg-wire-surface/95 border border-wire-border rounded-lg p-3 text-xs font-mono backdrop-blur">
              <div className="text-wire-muted uppercase tracking-wider text-[10px] mb-1.5">
                Last run
              </div>
              <ul className="space-y-0.5 max-h-40 overflow-y-auto">
                {runLog.map((e, i) => (
                  <li
                    key={i}
                    className={
                      e.status === 'error'
                        ? 'text-wire-eval'
                        : e.status === 'ok'
                          ? 'text-wire-data'
                          : 'text-wire-muted'
                    }
                  >
                    {e.status === 'ok' ? '✓' : e.status === 'error' ? '✗' : '…'} {e.nodeId}
                    {e.error && <span className="text-wire-muted"> — {e.error.message}</span>}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </main>
        <Inspector />
      </div>
      {galleryOpen && <TemplateGallery onClose={() => setGalleryOpen(false)} />}
    </div>
  );
}
