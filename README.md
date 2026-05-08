# 🧟 CyberZombie 桌面宠物

一个基于 **Python + PySide6 + React** 开发的赛博僵尸桌面宠物，具有像素风动画、系统监控、剪贴板监听、备忘录等功能。

![CyberZombie](assets/preview.png)

## ✨ 功能特性

- 🎭 **像素风精灵动画** — IDLE（待机）5帧 / WALK（行走）6帧序列动画
- 🖱️ **拖拽移动** — 支持鼠标拖拽，释放后有惯性滑动效果
- 📊 **系统感知** — 实时显示 CPU、内存、网络上下行速度
- 📋 **剪贴板监听** — 检测到复制内容时宠物进入狂暴模式
- 📝 **像素备忘录** — 双击宠物打开备忘录面板，支持添加/删除
- 🧲 **自动贴边** — 开启后宠物会自动吸附到屏幕边缘
- ⚙️ **右键菜单** — 状态切换、尺寸调节、动画速率、系统看板等

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+

### 安装依赖

```bash
# Python 依赖
pip install -r requirements.txt

# 前端依赖
cd frontend
npm install
npm run build
cd ..
```

### 运行

```bash
python main.py
```

## 📁 项目结构

```
.
├── main.py                 # 主入口（PySide6 窗口管理）
├── requirements.txt        # Python 依赖
├── backend/                # Python 后端
│   ├── web_channel.py      # QWebChannel 桥接
│   ├── monitor.py          # 系统监控
│   ├── clipboard_watcher.py # 剪贴板监听
│   └── storage.py          # 本地配置存储
├── frontend/               # React 前端
│   ├── src/
│   │   ├── components/     # UI 组件
│   │   ├── store/          # Zustand 状态管理
│   │   └── App.jsx         # 应用入口
│   └── dist/               # 构建产物
└── assets/                 # 精灵图资源
    ├── idle/               # 待机帧（5帧）
    └── walk/               # 行走帧（6帧）
```

## 🎮 操作说明

| 操作 | 说明 |
|------|------|
| 左键拖拽 | 移动宠物位置 |
| 左键单击 | 切换 IDLE / WALK 状态 |
| 左键双击 | 打开/关闭备忘录 |
| 右键 | 打开功能菜单 |
| 悬停 2秒 | 显示系统监控面板 |

## 🛠️ 技术栈

- **后端**：Python 3.12 + PySide6 + QWebEngineView + QWebChannel
- **前端**：React 19 + Vite + Tailwind CSS + Zustand
- **通信**：Qt Signals/Slots ↔ JavaScript 双向桥接

## 📝 需求文档

- [项目需求文档 (PRD)](🧟%20CyberZombie%20桌面宠物项目需求文档%20(PRD).md)
- [技术规格文档](🚀%20CyberZombie%20桌面宠物技术规格文档.md)

## 📄 License

MIT
