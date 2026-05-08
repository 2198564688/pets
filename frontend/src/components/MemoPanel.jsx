import React, { useState, useEffect } from 'react'
import { useStore } from '../store/useStore'

function MemoPanel() {
  const { showMemo, memos, setMemos, setShowMemo } = useStore()
  const [input, setInput] = useState('')

  useEffect(() => {
    if (!showMemo) return
    if (window.bridge?.loadSettings) {
      window.bridge.loadSettings().then((raw) => {
        try {
          const data = JSON.parse(raw)
          if (data.memos) setMemos(data.memos)
        } catch (e) {
          console.error(e)
        }
      })
    }
  }, [showMemo, setMemos])

  const handleAdd = () => {
    if (!input.trim()) return
    const newItem = {
      id: crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36),
      content: input.trim(),
      timestamp: new Date().toISOString(),
    }
    const currentMemos = useStore.getState().memos
    const next = [newItem, ...currentMemos]
    setMemos(next)
    setInput('')
    if (window.bridge?.saveMemo) {
      window.bridge.saveMemo(JSON.stringify(next))
    }
  }

  const handleDelete = (id) => {
    const currentMemos = useStore.getState().memos
    const next = currentMemos.filter((m) => m.id !== id)
    setMemos(next)
    if (window.bridge?.saveMemo) {
      window.bridge.saveMemo(JSON.stringify(next))
    }
  }

  const fmtTime = (iso) => {
    const d = new Date(iso)
    return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  }

  if (!showMemo) return null

  const panelStyle = {
    position: 'absolute',
    inset: 0,
    zIndex: 20,
    background: 'rgba(10,10,15,0.95)',
    border: '1px solid rgba(0,255,136,0.4)',
    padding: '10px',
    color: '#fff',
    fontFamily: 'monospace',
    fontSize: '12px',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
  }

  return (
    <div style={panelStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px', flexShrink: 0 }}>
        <span style={{ color: '#00ff88', fontWeight: 'bold', fontSize: '13px' }}>MEMO // 像素备忘录</span>
        <button
          style={{ background: 'transparent', border: 'none', color: '#ff4444', cursor: 'pointer', fontSize: '18px', padding: '0 4px', lineHeight: 1 }}
          onClick={() => setShowMemo(false)}
        >×</button>
      </div>

      <div style={{ display: 'flex', gap: '6px', marginBottom: '8px', flexShrink: 0 }}>
        <input
          style={{
            flex: 1, minWidth: 0,
            background: 'rgba(0,0,0,0.5)',
            border: '1px solid rgba(0,255,136,0.5)',
            borderRadius: '3px', padding: '5px 8px',
            color: '#fff', fontSize: '12px', outline: 'none', fontFamily: 'monospace',
          }}
          placeholder="输入备忘..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
        />
        <button
          style={{ background: '#00ff88', color: '#000', fontWeight: 'bold', padding: '5px 12px', borderRadius: '3px', border: 'none', cursor: 'pointer', fontSize: '13px', flexShrink: 0 }}
          onClick={handleAdd}
        >+</button>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', minHeight: 0 }}>
        {memos.map((m) => (
          <div key={m.id} style={{ background: 'rgba(0,0,0,0.4)', borderRadius: '3px', padding: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '5px', fontSize: '11px' }}>
            <div style={{ flex: 1, minWidth: 0, marginRight: '6px' }}>
              <div style={{ wordBreak: 'break-all', lineHeight: '1.4' }}>{m.content}</div>
              <div style={{ fontSize: '10px', color: '#888', marginTop: '3px' }}>{fmtTime(m.timestamp)}</div>
            </div>
            <button
              style={{ background: 'transparent', border: 'none', color: '#ff4444', cursor: 'pointer', fontSize: '16px', padding: '0 3px', flexShrink: 0 }}
              onClick={() => handleDelete(m.id)}
            >×</button>
          </div>
        ))}
        {memos.length === 0 && (
          <div style={{ color: '#555', textAlign: 'center', padding: '20px 0', fontSize: '12px' }}>暂无备忘，输入内容后按 + 添加</div>
        )}
      </div>
    </div>
  )
}

export default MemoPanel
