const TEMPLATES = [
  { slug: 'image-classifier', title: 'Image classifier', subtitle: 'Train a CLIP-backed classifier on uploaded photos. The classic Teachable Machine workflow.', tags: ['beginner', 'image'] },
  { slug: 'sound-classifier', title: 'Sound classifier', subtitle: 'Record short audio clips per class. Whisper-tiny embeds, linear head decides.', tags: ['beginner', 'audio'] },
  { slug: 'pose-classifier', title: 'Pose classifier', subtitle: 'MediaPipe landmarks → k-NN. Runs at camera framerate.', tags: ['beginner', 'pose'] },
  { slug: 'zero-shot-clip', title: 'Zero-shot classifier', subtitle: 'No labels required. Describe classes in text, CLIP does the rest.', tags: ['advanced', 'image'] },
];

function TemplateGallery({ onClose, onPick }) {
  const [filter, setFilter] = React.useState('all');
  const shown = TEMPLATES.filter(t => filter === 'all' || t.tags.includes(filter));
  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)',
      backdropFilter: 'blur(8px)', zIndex: 50,
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 32,
    }}>
      <div style={{
        background: 'var(--wire-surface)', border: '1px solid var(--wire-border)',
        borderRadius: 24, width: '100%', maxWidth: 720, overflow: 'hidden',
        boxShadow: '0 24px 64px -16px rgba(0,0,0,0.8)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start',
          padding: '20px 24px', borderBottom: '1px solid var(--wire-border)' }}>
          <div>
            <h2 style={{ fontSize: 18, fontWeight: 600, margin: 0 }}>Start from a template</h2>
            <p style={{ fontSize: 13, color: 'var(--wire-muted)', margin: '4px 0 0' }}>
              Every template is a pre-wired graph. Load, tweak, train.
            </p>
          </div>
          <button onClick={onClose} style={{
            padding: 8, background: 'transparent', border: 'none',
            borderRadius: 6, color: 'var(--wire-text)', cursor: 'pointer'
          }} onMouseEnter={e => e.currentTarget.style.background = 'var(--wire-surface-2)'}
             onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
            <i data-lucide="x" style={{ width: 18, height: 18 }}></i>
          </button>
        </div>
        <div style={{ padding: '16px 24px 0', display: 'flex', gap: 8 }}>
          {['all', 'beginner', 'advanced'].map(f => (
            <button key={f} onClick={() => setFilter(f)} style={{
              padding: '4px 12px', fontSize: 13, borderRadius: 999, border: 'none',
              cursor: 'pointer', fontFamily: 'var(--font-sans)',
              background: filter === f ? 'var(--wire-accent)' : 'var(--wire-surface-2)',
              color: filter === f ? 'white' : 'var(--wire-muted)',
            }}>{f[0].toUpperCase() + f.slice(1)}</button>
          ))}
        </div>
        <div style={{ padding: 24, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
          {shown.map(t => (
            <button key={t.slug} onClick={() => onPick?.(t)} style={{
              textAlign: 'left', padding: 16, background: 'var(--wire-surface-2)',
              border: '1px solid var(--wire-border)', borderRadius: 12,
              cursor: 'pointer', transition: 'border-color 200ms',
              fontFamily: 'var(--font-sans)', color: 'var(--wire-text)',
            }} onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--wire-accent)'}
               onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--wire-border)'}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <h3 style={{ fontSize: 14, fontWeight: 600, margin: 0 }}>{t.title}</h3>
                <i data-lucide="arrow-right" style={{ width: 14, height: 14, color: 'var(--wire-muted)' }}></i>
              </div>
              <p style={{ fontSize: 12, color: 'var(--wire-muted)', margin: 0, lineHeight: 1.55 }}>{t.subtitle}</p>
              <div style={{ display: 'flex', gap: 6, marginTop: 12 }}>
                {t.tags.map(tag => (
                  <span key={tag} style={{
                    fontFamily: 'var(--font-mono)', fontSize: 10, letterSpacing: '0.08em',
                    textTransform: 'uppercase', padding: '2px 8px', background: 'var(--wire-bg)',
                    border: '1px solid var(--wire-border)', borderRadius: 999, color: 'var(--wire-muted)',
                  }}>{tag}</span>
                ))}
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
window.TemplateGallery = TemplateGallery;
