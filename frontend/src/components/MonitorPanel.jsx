import { useStore } from '../store/useStore'

function MonitorPanel() {
  const { showMonitor, sysData } = useStore()

  if (!showMonitor) return null

  const panelStyle = {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 10,
    background: 'rgba(10,10,15,0.92)',
    borderBottom: '1px solid rgba(0,255,136,0.4)',
    padding: '8px 12px',
    color: '#fff',
    fontFamily: 'monospace',
    fontSize: '12px',
  }

  const barBg = {
    flex: 1,
    height: '8px',
    background: '#222',
    borderRadius: '4px',
    overflow: 'hidden',
  }

  const barFill = (pct) => ({
    width: `${Math.min(pct, 100)}%`,
    height: '100%',
    background: '#00ff88',
    borderRadius: '4px',
    transition: 'width 0.4s',
  })

  const rowStyle = {
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    marginBottom: '6px',
    whiteSpace: 'nowrap',
  }

  const labelStyle = {
    color: '#00ff88',
    fontWeight: 'bold',
    width: '36px',
    flexShrink: 0,
  }

  const valStyle = {
    width: '44px',
    flexShrink: 0,
    textAlign: 'right',
    fontSize: '13px',
  }

  return (
    <div style={panelStyle}>
      <div style={rowStyle}>
        <span style={labelStyle}>CPU</span>
        <div style={barBg}><div style={barFill(sysData.cpu)} /></div>
        <span style={valStyle}>{sysData.cpu}%</span>
      </div>
      <div style={rowStyle}>
        <span style={labelStyle}>MEM</span>
        <div style={barBg}><div style={barFill(sysData.mem)} /></div>
        <span style={valStyle}>{sysData.mem}%</span>
      </div>
      <div style={{ ...rowStyle, marginBottom: 0 }}>
        <span style={labelStyle}>NET</span>
        <span style={{ color: '#aaa', fontSize: '12px' }}>▲{sysData.up.toFixed(0)} ▼{sysData.down.toFixed(0)} KB/s</span>
      </div>
    </div>
  )
}

export default MonitorPanel
