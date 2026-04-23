function TopBar({ runtimeKind = 'web', onToggleRuntime, onRun, running, graphName = 'Untitled graph' }) {
  const isLocal = runtimeKind === 'local';
  return (
    <header style={{
      height: 48, display: 'flex', alignItems: 'center', gap: 12,
      padding: '0 16px', background: 'var(--wire-surface)',
      borderBottom: '1px solid var(--wire-border)', flexShrink: 0
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{
          width: 24, height: 24, borderRadius: 6,
          background: 'linear-gradient(135deg, #8b5cf6, #3b82f6)'
        }} />
        <span style={{ fontSize: 14, fontWeight: 600, letterSpacing: '-0.01em' }}>WireML</span>
      </div>

      <div style={{ height: 16, width: 1, background: 'var(--wire-border)' }} />

      <div style={{ fontSize: 14, color: 'var(--wire-muted)', maxWidth: 240,
        overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{graphName}</div>

      <button className="btn-ghost" style={{ marginLeft: 4 }}>
        <i data-lucide="layers" style={{ width: 14, height: 14 }}></i>
        Templates
      </button>

      <div style={{ flex: 1 }} />

      <div style={{
        display: 'inline-flex', alignItems: 'center', gap: 6,
        padding: '4px 10px', borderRadius: 999, border: '1px solid',
        fontSize: 11, fontWeight: 500, letterSpacing: '0.04em',
        background: isLocal ? 'rgba(245,158,11,0.1)' : 'rgba(59,130,246,0.1)',
        borderColor: isLocal ? '#f59e0b' : '#3b82f6',
        color: isLocal ? '#f59e0b' : '#3b82f6',
      }}>
        <i data-lucide="cpu" style={{ width: 12, height: 12 }}></i>
        <span style={{ textTransform: 'uppercase' }}>{isLocal ? 'Power mode' : 'Web mode'}</span>
        <span style={{ color: 'var(--wire-muted)' }}>· {isLocal ? 'cuda' : 'webgpu'}</span>
      </div>

      <button className="btn-ghost" onClick={onToggleRuntime}>
        <i data-lucide="arrow-left-right" style={{ width: 14, height: 14 }}></i>
        Toggle
      </button>

      <button className="btn-primary" onClick={onRun} disabled={running}>
        {running
          ? <><i data-lucide="loader-circle" style={{ width: 14, height: 14, animation: 'spin 1s linear infinite' }}></i> Running…</>
          : <><i data-lucide="play" style={{ width: 14, height: 14 }}></i> Run graph</>}
      </button>
    </header>
  );
}
window.TopBar = TopBar;
