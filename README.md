# 🧟 CyberZombie 桌面宠物

> 一个能感知系统环境并主动提供情绪与效率价值的伴侣型桌面宠物。

## 💡 项目背景

个人开发者或创作者在沉浸式工作（如编译代码、跑模型）时，常因频繁切换窗口来查看系统资源或待办事项（Memo）而打断心流。现有监控软件过于机械，而传统桌面宠物缺乏实用价值。本项目通过 AI Agent 将**系统状态监控**与**任务管理**结合，提供一个能感知系统环境并主动提供情绪与效率价值的伴侣型工具。

## 🧠 核心架构：多 Agent 异步协作

项目采用 Python (PySide6) 构建，底层舍弃了高延迟的单次 LLM 对话，而是设计了一个低开销的多 Agent 异步协作流：

### 感知智能体（Sensor Agent）
负责底层数据采集。实时获取 CPU/内存占用、网络状态，并同步本地极简 Memo 的待办列表。

### 推理智能体（Reasoner Agent）
负责长链上下文分析。它不会简单复述数据，而是进行逻辑推导：
> 感知到 CPU 持续高负载 + 本地存在"打包测试"的待办 → 推理出"用户正在编译重度项目" → 结合当前连续工作时长 → 决策出交互策略（如：不弹窗打扰，但改变宠物状态）。

### 执行智能体（Actor Agent）
接收推理指令后，动态调整桌面 UI 的像素级动画（如切换到"流汗/努力"状态），并在合适的时机生成简短、拟人化的 Tips：
> "资源占用率已达 85%，编译快结束啦，先喝口水吧"

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
