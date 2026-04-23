const LIB_CATEGORIES = [
  { id: 'data', label: 'Data sources', items: [
    { id: 'data.webcam', name: 'Webcam', icon: 'camera' },
    { id: 'data.upload', name: 'Upload Images', icon: 'upload' },
    { id: 'data.mic', name: 'Microphone', icon: 'mic' },
  ]},
  { id: 'backbone', label: 'Backbones', items: [
    { id: 'backbone.clip.vit-b-32', name: 'CLIP ViT-B/32 (image)', icon: 'brain' },
    { id: 'backbone.clip.text-vit-b-32', name: 'CLIP ViT-B/32 (text)', icon: 'type' },
    { id: 'backbone.dinov2.small', name: 'DINOv2 ViT-S/14', icon: 'eye' },
    { id: 'backbone.mobilenet.v3', name: 'MobileNetV3', icon: 'smartphone' },
    { id: 'backbone.whisper.tiny', name: 'Whisper tiny (encoder)', icon: 'audio-waveform' },
    { id: 'backbone.mediapipe.pose', name: 'MediaPipe Pose', icon: 'person-standing' },
    { id: 'backbone.clip.vit-l-14', name: 'CLIP ViT-L/14 (image)', icon: 'brain', localOnly: true },
  ]},
  { id: 'head', label: 'Heads', items: [
    { id: 'head.linear', name: 'Linear Classifier', icon: 'calculator' },
    { id: 'head.knn', name: 'k-NN', icon: 'network' },
    { id: 'head.zeroshot-clip', name: 'Zero-Shot CLIP', icon: 'sparkles' },
  ]},
  { id: 'eval', label: 'Evaluation', items: [
    { id: 'eval.accuracy', name: 'Accuracy', icon: 'target' },
    { id: 'eval.confusion', name: 'Confusion Matrix', icon: 'grid-3x3' },
  ]},
  { id: 'deploy', label: 'Deploy', items: [
    { id: 'deploy.preview', name: 'Live Preview', icon: 'monitor' },
    { id: 'deploy.export-onnx', name: 'Export ONNX', icon: 'download' },
    { id: 'deploy.share-url', name: 'Shareable URL', icon: 'link-2' },
  ]},
];

function NodeLibrary({ onAdd, powerMode = false }) {
  const [q, setQ] = React.useState('');
  const filtered = LIB_CATEGORIES.map(c => ({
    ...c, items: c.items.filter(i => !q || i.name.toLowerCase().includes(q.toLowerCase()))
  })).filter(c => c.items.length);
  return (
    <aside style={{
      width: 272, background: 'var(--wire-surface)',
      borderRight: '1px solid var(--wire-border)',
      display: 'flex', flexDirection: 'column', flexShrink: 0,
    }}>
      <div style={{ padding: 12, borderBottom: '1px solid var(--wire-border)' }}>
        <h2 className="overline" style={{ margin: '0 0 8px' }}>Node library</h2>
        <div style={{ position: 'relative' }}>
          <i data-lucide="search" style={{ width: 14, height: 14, position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)', color: 'var(--wire-muted)' }}></i>
          <input value={q} onChange={e => setQ(e.target.value)} placeholder="Search nodes..." style={{
            width: '100%', padding: '6px 8px 6px 32px', fontSize: 13,
            background: 'var(--wire-surface-2)', border: '1px solid var(--wire-border)',
            borderRadius: 6, color: 'var(--wire-text)', outline: 'none', boxSizing: 'border-box',
            fontFamily: 'var(--font-sans)'
          }}/>
        </div>
      </div>
      <div style={{ flex: 1, overflowY: 'auto', padding: '8px 8px' }}>
        {filtered.map(cat => (
          <section key={cat.id} style={{ marginBottom: 16 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '4px 8px' }}>
              <span className={`category-dot ${cat.id}`}/>
              <h3 className="overline" style={{ margin: 0, fontWeight: 600 }}>{cat.label}</h3>
              <span style={{ marginLeft: 'auto', fontFamily: 'var(--font-mono)', fontSize: 10, color: 'var(--wire-muted)' }}>{cat.items.length}</span>
            </div>
            <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
              {cat.items.map(item => {
                const disabled = item.localOnly && !powerMode;
                return (
                  <li key={item.id}>
                    <button disabled={disabled} onClick={() => onAdd?.(item)} style={{
                      width: '100%', display: 'flex', alignItems: 'center', gap: 8,
                      padding: '6px 8px', borderRadius: 6, background: 'transparent',
                      border: 'none', textAlign: 'left', fontSize: 13,
                      color: disabled ? 'var(--wire-muted)' : 'var(--wire-text)',
                      cursor: disabled ? 'not-allowed' : 'pointer',
                      fontFamily: 'var(--font-sans)', transition: 'background 120ms',
                    }} onMouseEnter={e => !disabled && (e.currentTarget.style.background = 'var(--wire-surface-2)')}
                       onMouseLeave={e => e.currentTarget.style.background = 'transparent'}>
                      <i data-lucide={item.icon} style={{ width: 14, height: 14, color: 'var(--wire-muted)', flexShrink: 0 }}></i>
                      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{item.name}</span>
                      {disabled && <i data-lucide="lock" style={{ width: 11, height: 11, color: 'var(--wire-muted)', marginLeft: 'auto' }}></i>}
                    </button>
                  </li>
                );
              })}
            </ul>
          </section>
        ))}
      </div>
    </aside>
  );
}
window.NodeLibrary = NodeLibrary;
