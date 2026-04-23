function Inspector({ node }) {
  if (!node) {
    return (
      <aside style={{
        width: 300, background: 'var(--wire-surface)',
        borderLeft: '1px solid var(--wire-border)', padding: 16,
        fontSize: 13, color: 'var(--wire-muted)', flexShrink: 0,
      }}>
        <p style={{ margin: 0 }}>Select a node to configure.</p>
      </aside>
    );
  }
  return (
    <aside style={{
      width: 300, background: 'var(--wire-surface)',
      borderLeft: '1px solid var(--wire-border)',
      display: 'flex', flexDirection: 'column', flexShrink: 0, overflow: 'hidden'
    }}>
      <div style={{ padding: 16, borderBottom: '1px solid var(--wire-border)' }}>
        <div className="overline" style={{ margin: 0 }}>{node.category}</div>
        <div style={{ fontSize: 16, fontWeight: 600, marginTop: 2 }}>{node.name}</div>
        <div style={{ fontSize: 12, color: 'var(--wire-muted)', marginTop: 6, lineHeight: 1.5 }}>{node.description}</div>
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: 16 }}>
        {(node.params || []).map(p => (
          <div key={p.name} style={{ marginBottom: 12 }}>
            <label className="overline" style={{ display: 'block', marginBottom: 4 }}>{p.label || p.name}</label>
            {p.kind === 'enum' ? (
              <select defaultValue={p.default} style={inputStyle}>
                {p.options.map(o => <option key={o}>{o}</option>)}
              </select>
            ) : p.kind === 'boolean' ? (
              <label style={{ display: 'inline-flex', alignItems: 'center', gap: 8, fontSize: 13 }}>
                <input type="checkbox" defaultChecked={p.default} style={{ accentColor: 'var(--wire-accent)' }}/>
                <span>{p.default ? 'On' : 'Off'}</span>
              </label>
            ) : (
              <input type={p.kind === 'number' ? 'number' : 'text'} defaultValue={p.default} style={inputStyle}/>
            )}
          </div>
        ))}
      </div>
    </aside>
  );
}
const inputStyle = {
  width: '100%', padding: '6px 8px', fontSize: 13,
  background: 'var(--wire-surface-2)', border: '1px solid var(--wire-border)',
  borderRadius: 6, color: 'var(--wire-text)', outline: 'none', boxSizing: 'border-box',
  fontFamily: 'var(--font-sans)',
};
window.Inspector = Inspector;
