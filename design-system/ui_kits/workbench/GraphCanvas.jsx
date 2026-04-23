const CAT_COLOR = {
  data: '#10b981', backbone: '#3b82f6', head: '#f59e0b',
  eval: '#ef4444', deploy: '#14b8a6', preprocess: '#8b5cf6',
};

function NodeCard({ node, selected, onSelect }) {
  const color = CAT_COLOR[node.category];
  return (
    <div onClick={() => onSelect?.(node.id)} style={{
      position: 'absolute', left: node.x, top: node.y,
      minWidth: 200, background: 'var(--wire-surface)',
      borderRadius: 12, overflow: 'hidden', cursor: 'pointer',
      border: `1px solid ${color}`,
      background: `linear-gradient(${color}14, ${color}14), var(--wire-surface)`,
      boxShadow: selected
        ? `0 0 0 2px ${color}, 0 4px 32px -4px ${color}80`
        : '0 4px 24px -4px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.04)',
      transition: 'box-shadow 200ms',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8,
        padding: '8px 12px', borderBottom: '1px solid var(--wire-border)' }}>
        <i data-lucide={node.icon} style={{ width: 14, height: 14, color }}></i>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 10, fontWeight: 600,
          letterSpacing: '0.12em', textTransform: 'uppercase', color: 'var(--wire-muted)' }}>
          {node.category}
        </span>
      </div>
      <div style={{ padding: '10px 12px' }}>
        <div style={{ fontSize: 14, fontWeight: 600 }}>{node.name}</div>
        <div style={{ fontSize: 11, color: 'var(--wire-muted)', marginTop: 2, lineHeight: 1.4 }}>
          {node.description}
        </div>
      </div>
      <div style={{ padding: '6px 12px', borderTop: '1px solid var(--wire-border)',
        background: 'rgba(26,34,45,0.4)', fontFamily: 'var(--font-mono)',
        fontSize: 10, color: 'var(--wire-muted)', textTransform: 'uppercase',
        letterSpacing: '0.08em', display: 'flex', justifyContent: 'space-between' }}>
        <span>{node.mode === 'reactive' ? '◉ reactive' : '▶ triggered'}</span>
        {node.localOnly && <span style={{ color: '#f59e0b' }}>Local only</span>}
      </div>
      {/* handles */}
      {node.inputs?.map((_, i) => (
        <span key={'in'+i} style={handleStyle(-5, 60 + i*22)}/>
      ))}
      {node.outputs?.map((_, i) => (
        <span key={'out'+i} style={{ ...handleStyle(0, 60 + i*22), right: -5, left: 'auto' }}/>
      ))}
    </div>
  );
}

function handleStyle(left, top) {
  return {
    position: 'absolute', left, top, width: 10, height: 10,
    border: '2px solid var(--wire-bg)', background: 'var(--wire-muted)',
    borderRadius: '50%',
  };
}

function Wires({ nodes, edges }) {
  const byId = Object.fromEntries(nodes.map(n => [n.id, n]));
  return (
    <svg style={{ position: 'absolute', inset: 0, pointerEvents: 'none', width: '100%', height: '100%' }}>
      {edges.map((e, i) => {
        const s = byId[e.source]; const t = byId[e.target];
        if (!s || !t) return null;
        const sx = s.x + 200, sy = s.y + 60;
        const tx = t.x, ty = t.y + 60;
        const mx = (sx + tx) / 2;
        return (
          <path key={i}
            d={`M${sx} ${sy} C ${mx} ${sy}, ${mx} ${ty}, ${tx} ${ty}`}
            stroke={CAT_COLOR[s.category] || '#6c7a8c'} strokeWidth={1.5}
            fill="none" opacity={0.85}
          />
        );
      })}
    </svg>
  );
}

function GraphCanvas({ nodes, edges, selectedId, onSelect }) {
  return (
    <div style={{
      position: 'relative', flex: 1, overflow: 'hidden',
      backgroundColor: 'var(--wire-bg)',
      backgroundImage: 'radial-gradient(circle, #1a222d 1px, transparent 1px)',
      backgroundSize: '24px 24px',
    }}>
      <Wires nodes={nodes} edges={edges}/>
      {nodes.map(n => (
        <NodeCard key={n.id} node={n} selected={n.id === selectedId} onSelect={onSelect}/>
      ))}
      {/* bottom-left controls */}
      <div style={{ position: 'absolute', bottom: 16, left: 16,
        background: 'var(--wire-surface)', border: '1px solid var(--wire-border)',
        borderRadius: 6, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
        {['plus', 'minus', 'maximize-2', 'lock'].map(icon => (
          <button key={icon} style={ctrlBtn}>
            <i data-lucide={icon} style={{ width: 12, height: 12 }}></i>
          </button>
        ))}
      </div>
      {/* bottom-right hud */}
      <div style={{ position: 'absolute', bottom: 16, right: 16,
        background: 'rgba(19,25,33,0.95)', border: '1px solid var(--wire-border)',
        borderRadius: 10, padding: '8px 12px', fontFamily: 'var(--font-mono)',
        fontSize: 11, color: 'var(--wire-muted)', backdropFilter: 'blur(12px)' }}>
        graph.nodes: <span style={{ color: 'var(--wire-text)' }}>{nodes.length}</span>
        {' · '}edges: <span style={{ color: 'var(--wire-text)' }}>{edges.length}</span>
        {' · '}runtime: <span style={{ color: 'var(--wire-accent)' }}>webgpu</span>
      </div>
    </div>
  );
}
const ctrlBtn = {
  width: 28, height: 28, background: 'transparent', border: 'none',
  borderBottom: '1px solid var(--wire-border)', color: 'var(--wire-text)',
  cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
};
window.GraphCanvas = GraphCanvas;
