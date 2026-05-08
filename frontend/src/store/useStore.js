import { create } from 'zustand'

export const useStore = create((set, get) => ({
  // 动画状态
  petState: 'IDLE',
  setPetState: (s) => set({ petState: s }),

  // 缩放与帧率
  scale: 0.5,
  setScale: (v) => set({ scale: v }),
  fps: 15,
  setFps: (v) => set({ fps: v }),

  // 系统数据
  sysData: { cpu: 0, mem: 0, up: 0, down: 0 },
  setSysData: (d) => set({ sysData: d }),

  // 监控面板
  showMonitor: false,
  setShowMonitor: (v) => set({ showMonitor: v }),

  // 备忘录
  showMemo: false,
  setShowMemo: (v) => set({ showMemo: v }),
  memos: [],
  setMemos: (list) => set({ memos: list }),

  // 配置
  config: {},
  setConfig: (c) => set({ config: c }),

  // 翻转
  facingRight: true,
  setFacingRight: (v) => set({ facingRight: v }),

  // 点击穿透
  clickThrough: false,
  setClickThrough: (v) => set({ clickThrough: v }),

  // 自动贴边（吸附）
  autoHide: false,
  setAutoHide: (v) => set({ autoHide: v }),
}))
