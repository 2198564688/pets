import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { useStore } from '../store/useStore'

const IDLE_FRAMES = 5
const WALK_FRAMES = 6
const STATE_DIMS = {
  IDLE: { w: 172, h: 471 },
  WALK: { w: 187, h: 384 },
  PANIC: { w: 172, h: 471 },
}
const MAX_W = 187
const MAX_H = 471

function Pet() {
  const { petState, scale, fps, facingRight, showMemo, setShowMemo, setShowMonitor } = useStore()
  const [frame, setFrame] = useState(0)
  const [panicBlink, setPanicBlink] = useState(false)
  const canvasRef = useRef(null)
  const imagesRef = useRef({ idle: [], walk: [] })
  const loadedRef = useRef(false)

  // 预加载图片
  useEffect(() => {
    if (loadedRef.current) return
    loadedRef.current = true
    const load = (prefix, count) => {
      return Array.from({ length: count }, (_, i) => {
        const img = new Image()
        const fileName = `${prefix}_${String(i).padStart(2, '0')}.png`
        // public/assets 下的文件会被复制到 dist/assets，相对 index.html 直接用 ./assets/... 即可
        img.src = `./assets/${prefix}/${fileName}`
        img.onerror = () => console.error('Failed to load', img.src)
        return img
      })
    }
    imagesRef.current.idle = load('idle', IDLE_FRAMES)
    imagesRef.current.walk = load('walk', WALK_FRAMES)
  }, [])

  // 动画循环 —— ref 计数避免 React setState 批处理丢帧
  const frameRef = useRef(0)
  const panicRef = useRef(false)

  useEffect(() => {
    let raf
    let last = 0
    const panicMult = petState === 'PANIC' ? 2 : 1
    const interval = 1000 / (fps * panicMult)
    const count = petState === 'WALK' ? WALK_FRAMES : IDLE_FRAMES

    const loop = (ts) => {
      if (ts - last >= interval) {
        last = ts
        frameRef.current = (frameRef.current + 1) % count
        setFrame(frameRef.current)
        if (petState === 'PANIC') {
          panicRef.current = !panicRef.current
          setPanicBlink(panicRef.current)
        } else if (panicRef.current) {
          panicRef.current = false
          setPanicBlink(false)
        }
      }
      raf = requestAnimationFrame(loop)
    }
    raf = requestAnimationFrame(loop)
    return () => cancelAnimationFrame(raf)
  }, [petState, fps])

  // Canvas 绘制
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const dims = STATE_DIMS[petState] || STATE_DIMS.IDLE
    const canvasW = Math.round(MAX_W * scale)
    const canvasH = Math.round(MAX_H * scale)
    canvas.width = canvasW
    canvas.height = canvasH
    ctx.clearRect(0, 0, canvasW, canvasH)

    const imgs = petState === 'WALK' ? imagesRef.current.walk : imagesRef.current.idle
    const img = imgs[frame]
    if (!img || !img.complete || img.naturalWidth === 0) return

    ctx.imageSmoothingEnabled = false

    if (petState === 'PANIC' && panicBlink) {
      ctx.filter = 'brightness(1.5) sepia(1) saturate(3) hue-rotate(-50deg)'
    } else {
      ctx.filter = 'none'
    }

    const drawW = Math.round(dims.w * scale)
    const drawH = Math.round(dims.h * scale)
    const offsetX = Math.round((MAX_W - dims.w) / 2 * scale)
    const offsetY = Math.round((MAX_H - dims.h) * scale)

    ctx.save()
    if (!facingRight) {
      ctx.translate(canvasW, 0)
      ctx.scale(-1, 1)
      ctx.drawImage(img, canvasW - offsetX - drawW, offsetY, drawW, drawH)
    } else {
      ctx.drawImage(img, offsetX, offsetY, drawW, drawH)
    }
    ctx.restore()
  }, [frame, petState, scale, facingRight, panicBlink])

  const clickTimerRef = useRef(null)

  const handleToggleState = () => {
    const next = petState === 'IDLE' ? 'WALK' : 'IDLE'
    if (window.bridge) window.bridge.setPetState(next)
    useStore.getState().setPetState(next)
  }

  const handleDoubleClick = (e) => {
    e.stopPropagation()
    if (clickTimerRef.current) {
      clearTimeout(clickTimerRef.current)
      clickTimerRef.current = null
    }
    setShowMemo(!showMemo)
  }

  const hoverTimerRef = useRef(null)
  const handleMouseEnter = () => {
    hoverTimerRef.current = setTimeout(() => setShowMonitor(true), 2000)
    if (window.bridge) window.bridge.peekOut()
  }
  const handleMouseLeave = () => {
    clearTimeout(hoverTimerRef.current)
    setShowMonitor(false)
  }

  const dragState = useRef({ isDown: false, startX: 0, startY: 0, hasDragged: false, dragNotified: false })
  const dragThreshold = 5

  const handleMouseDown = (e) => {
    dragState.current = { isDown: true, startX: e.clientX, startY: e.clientY, hasDragged: false, dragNotified: false }
  }

  const handleMouseMove = (e) => {
    if (!dragState.current.isDown) return
    const dx = Math.abs(e.clientX - dragState.current.startX)
    const dy = Math.abs(e.clientY - dragState.current.startY)
    if (dx > dragThreshold || dy > dragThreshold) {
      if (!dragState.current.dragNotified) {
        dragState.current.dragNotified = true
        dragState.current.hasDragged = true
        if (window.bridge) window.bridge.startDrag()
      }
    }
  }

  const handleMouseUp = () => {
    if (!dragState.current.isDown) return
    dragState.current.isDown = false
    if (dragState.current.dragNotified && window.bridge) {
      window.bridge.endDrag()
    }
    if (!dragState.current.hasDragged) {
      if (clickTimerRef.current) {
        clearTimeout(clickTimerRef.current)
        clickTimerRef.current = null
        return
      }
      clickTimerRef.current = setTimeout(() => {
        clickTimerRef.current = null
        handleToggleState()
      }, 280)
    }
  }

  return (
    <motion.div
      className="relative"
      style={{ width: MAX_W * scale, height: MAX_H * scale, cursor: 'grab', touchAction: 'none', userSelect: 'none' }}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onDoubleClick={handleDoubleClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      whileTap={{ cursor: 'grabbing' }}
    >
      <canvas
        ref={canvasRef}
        className="pixel-shadow"
        style={{
          width: MAX_W * scale,
          height: MAX_H * scale,
          display: 'block',
          willChange: 'transform',
        }}
      />
    </motion.div>
  )
}

export default Pet
