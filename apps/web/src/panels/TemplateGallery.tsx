import { useState } from 'react';
import * as icons from 'lucide-react';
import { TEMPLATES } from '@wireml/templates';
import { useGraphStore } from '@/store/graphStore';
import clsx from 'clsx';

interface TemplateGalleryProps {
  onClose: () => void;
}

export function TemplateGallery({ onClose }: TemplateGalleryProps) {
  const [filter, setFilter] = useState<'all' | 'beginner' | 'advanced'>('all');
  const setGraph = useGraphStore((s) => s.setGraph);

  const shown = TEMPLATES.filter(
    (t) => filter === 'all' || t.tags.includes(filter),
  );

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-8">
      <div className="bg-wire-surface border border-wire-border rounded-2xl w-full max-w-3xl overflow-hidden shadow-2xl">
        <div className="flex items-center justify-between px-6 py-4 border-b border-wire-border">
          <div>
            <h2 className="text-lg font-semibold">Start from a template</h2>
            <p className="text-sm text-wire-muted mt-0.5">
              Every template is a pre-wired graph. Load, tweak, train.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-wire-surface-2 rounded-md transition-colors"
            aria-label="Close"
          >
            <icons.X size={18} />
          </button>
        </div>

        <div className="px-6 pt-4 flex gap-2">
          {(['all', 'beginner', 'advanced'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={clsx(
                'px-3 py-1 text-sm rounded-full transition-colors',
                filter === f
                  ? 'bg-wire-accent text-white'
                  : 'bg-wire-surface-2 text-wire-muted hover:text-wire-text',
              )}
            >
              {f[0]!.toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>

        <div className="p-6 grid grid-cols-2 gap-3">
          {shown.map((t) => (
            <button
              key={t.slug}
              onClick={() => {
                setGraph(t.graph);
                onClose();
              }}
              className="text-left p-4 bg-wire-surface-2 hover:bg-wire-surface-2/80 border border-wire-border hover:border-wire-accent rounded-xl transition-all"
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold">{t.title}</h3>
                <icons.ArrowRight size={14} className="text-wire-muted" />
              </div>
              <p className="text-xs text-wire-muted leading-relaxed line-clamp-2">
                {t.subtitle}
              </p>
              <div className="flex gap-1.5 mt-3">
                {t.tags.map((tag) => (
                  <span
                    key={tag}
                    className="text-[10px] uppercase tracking-wide px-2 py-0.5 bg-wire-bg rounded-full text-wire-muted border border-wire-border"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
