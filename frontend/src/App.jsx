import { useEffect, useRef } from 'react'
import Pet from './components/Pet'
import MonitorPanel from './components/MonitorPanel'
import MemoPanel from './components/MemoPanel'
import ContextMenu from './components/ContextMenu'
import { useStore } from './store/useStore'

function App() {
  const { setSysData, setConfig, setScale, setFps, setPetState, setFacingRight, setAutoHide, showMonitor, showMemo } = useStore()
  const panicTimerRef = useRef(null)
  const prePanicStateRef = useRef('IDLE')

  useEffect(() => {
    if (window.qt && window.qt.webChannelTransport) {
      new window.QWebChannel(window.qt.webChannelTransport, (channel) => {
        window.bridge = channel.objects.bridge

        window.bridge.loadSettings().then((raw) => {
          try {
            const data = JSON.parse(raw)
            setConfig(data.config || {})
            if (data.config) {
              setScale(data.config.scale ?? 1.0)
              setFps(data.config.fps ?? 15)
              setPetState(data.config.state ?? 'IDLE')
              setAutoHide(data.config.auto_hide ?? false)
            }
          } catch (e) {
            console.error(e)
          }
        })

        window.bridge.sysUpdate.connect((data) => {
          setSysData(data)
        })

        window.bridge.clipboardAlert.connect((_data) => {
          const current = useStore.getState().petState
          if (current !== 'PANIC') {
            prePanicStateRef.current = current
          } else if (!panicTimerRef.current) {
            return
          }
          setPetState('PANIC')
          if (window.bridge) window.bridge.setPetState('PANIC')
          if (panicTimerRef.current) clearTimeout(panicTimerRef.current)
          panicTimerRef.current = setTimeout(() => {
            panicTimerRef.current = null
            const restore = prePanicStateRef.current === 'PANIC' ? 'IDLE' : prePanicStateRef.current
            setPetState(restore)
            if (window.bridge) window.bridge.setPetState(restore)
          }, 3000)
        })

        window.bridge.directionChanged.connect((right) => {
          setFacingRight(right)
        })
        window.bridge.stateChanged.connect((state) => {
          setPetState(state)
        })
      })
    }
  }, [setSysData, setConfig, setScale, setFps, setPetState, setFacingRight, setAutoHide])

  useEffect(() => {
    if (window.bridge?.setPanelLayout) {
      window.bridge.setPanelLayout(showMonitor, showMemo)
    }
  }, [showMonitor, showMemo])

  return (
    <div className="relative w-full h-full">
      <MonitorPanel />
      <div className="w-full h-full flex items-end justify-center">
        <Pet />
      </div>
      <MemoPanel />
      <ContextMenu />
    </div>
  )
}

export default App
