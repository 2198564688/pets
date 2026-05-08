import React, { useState, useEffect, useRef } from 'react'
import { useStore } from '../store/useStore'

function ContextMenu() {
  const [visible, setVisible] = useState(false)
  const [pos, setPos] = useState({ x: 0, y: 0 })
  const [openSub, setOpenSub] = useState(null)
  const menuRef = useRef(null)

  const {
    petState, setPetState, scale, setScale, fps, setFps,
    autoHide, setAutoHide, showMonitor, setShowMonitor, setMemos
  } = useStore()

  useEffect(() => {
    const onContext = (e) => {
      e.preventDefault()
      setPos({ x: e.clientX, y: e.clientY })
      setVisible(true)
      setOpenSub(null)
    }
    const onMouseDown = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setVisible(false)
        setOpenSub(null)
      }
    }
    window.addEventListener('contextmenu', onContext)
    window.addEventListener('mousedown', onMouseDown)
    return () => {
      window.removeEventListener('contextmenu', onContext)
      window.removeEventListener('mousedown', onMouseDown)
    }
  }, [])

  // 计算菜单位置，确保不超出窗口
  const vw = window.innerWidth
  const vh = window.innerHeight
  const menuW = 140
  let mx = pos.x
  let my = pos.y
  if (mx + menuW > vw) mx = vw - menuW - 4
  if (mx < 0) mx = 4
  if (my < 0) my = 4

  const handleAction = (fn) => {
    fn()
    setVisible(false)
    setOpenSub(null)
  }

  const toggleSub = (idx) => {
    setOpenSub(openSub === idx ? null : idx)
  }

  const menuStyle = {
    position: 'fixed',
    left: mx,
    top: my,
    width: menuW,
    zIndex: 9999,
    maxHeight: vh - my - 8,
    overflowY: 'auto',
    background: 'rgba(10,10,15,0.95)',
    border: '1px solid rgba(0,255,136,0.3)',
    borderRadius: '4px',
    padding: '4px 0',
    fontSize: '12px',
    color: '#fff',
    fontFamily: 'monospace',
    userSelect: 'none',
    pointerEvents: 'auto',
  }

  const itemStyle = {
    padding: '6px 12px',
    cursor: 'pointer',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  }

  const activeStyle = { color: '#00ff88' }
  const hoverStyle = { background: 'rgba(255,255,255,0.08)' }

  const subMenuStyle = {
    background: 'rgba(10,10,15,0.95)',
    border: '1px solid rgba(0,255,136,0.3)',
    borderRadius: '4px',
    padding: '4px 0',
    marginTop: '2px',
  }

  const renderItem = (label, onClick, active = false, hasChildren = false) => (
    <div
      key={label}
      style={itemStyle}
      className="menu-item"
      onMouseDown={(e) => {
        e.stopPropagation()
        e.preventDefault()
        onClick()
      }}
      onMouseEnter={(e) => { e.currentTarget.style.background = hoverStyle.background }}
      onMouseLeave={(e) => { e.currentTarget.style.background = 'transparent' }}
    >
      <span style={active ? activeStyle : {}}>{label}</span>
      {hasChildren && <span style={{ fontSize: '10px', color: '#888' }}>▶</span>}
    </div>
  )

  if (!visible) return null

  return (
    <div ref={menuRef} style={menuStyle}>
      {/* 状态切换 */}
      {renderItem('状态切换', () => toggleSub(0), false, true)}
      {openSub === 0 && (
        <div style={subMenuStyle}>
          {renderItem('IDLE', () => handleAction(() => { window.bridge?.setPetState('IDLE'); setPetState('IDLE') }), petState === 'IDLE')}
          {renderItem('WALK', () => handleAction(() => { window.bridge?.setPetState('WALK'); setPetState('WALK') }), petState === 'WALK')}
          {renderItem('狂暴模式', () => handleAction(() => { window.bridge?.setPetState('PANIC'); setPetState('PANIC') }), petState === 'PANIC')}
        </div>
      )}

      {/* 显示尺寸 */}
      {renderItem('显示尺寸', () => toggleSub(1), false, true)}
      {openSub === 1 && (
        <div style={subMenuStyle}>
          {[0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0].map((v) =>
            renderItem(`${v}x`, () => handleAction(() => { window.bridge?.setScale(v); setScale(v) }), Math.abs(scale - v) < 0.01)
          )}
        </div>
      )}

      {/* 动画速率 */}
      {renderItem('动画速率', () => toggleSub(2), false, true)}
      {openSub === 2 && (
        <div style={subMenuStyle}>
          {renderItem('慢 (10fps)', () => handleAction(() => { setFps(10); window.bridge?.saveConfig(JSON.stringify({fps: 10})) }), fps === 10)}
          {renderItem('标准 (15fps)', () => handleAction(() => { setFps(15); window.bridge?.saveConfig(JSON.stringify({fps: 15})) }), fps === 15)}
          {renderItem('标准 (24fps)', () => handleAction(() => { setFps(24); window.bridge?.saveConfig(JSON.stringify({fps: 24})) }), fps === 24)}
          {renderItem('极速 (60fps)', () => handleAction(() => { setFps(60); window.bridge?.saveConfig(JSON.stringify({fps: 60})) }), fps === 60)}
        </div>
      )}

      {/* 系统看板 */}
      {renderItem(showMonitor ? '✓ 系统看板' : '系统看板', () => handleAction(() => setShowMonitor(!showMonitor)), showMonitor)}

      {/* 自动贴边 */}
      {renderItem(autoHide ? '✓ 自动贴边' : '自动贴边', () => handleAction(() => {
        const next = !autoHide
        window.bridge?.setAutoHide(next)
        setAutoHide(next)
      }), autoHide)}

      {/* 数据管理 */}
      {renderItem('数据管理', () => toggleSub(4), false, true)}
      {openSub === 4 && (
        <div style={subMenuStyle}>
          {renderItem('导出备忘录', () => handleAction(() => {
            const data = JSON.stringify(useStore.getState().memos, null, 2)
            const blob = new Blob([data], { type: 'application/json' })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = 'cyberzombie_memos.json'
            a.click()
            URL.revokeObjectURL(url)
          }))}
          {renderItem('清除缓存', () => handleAction(() => {
            if (window.confirm('确定要清空所有备忘录吗？')) {
              setMemos([])
              window.bridge?.saveMemo('[]')
            }
          }))}
        </div>
      )}

      {/* 退出 */}
      {renderItem('退出', () => handleAction(() => window.bridge?.exitApp()))}
    </div>
  )
}

export default ContextMenu
