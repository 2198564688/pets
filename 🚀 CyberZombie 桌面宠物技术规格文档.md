# 🚀 CyberZombie 桌面宠物技术规格文档

## 1. 系统架构设计 (System Architecture)

采用 **后端控制与数据采样 (Python)** + **前端渲染与动效 (React/Vite)** 的混合模式。

- **Host Environment:** Windows 10/11 (自带 WebView2)
- **Core Framework:** **Python 3.11+** + **PySide6** (原生多窗口管理、系统 API 绑定、`QWebEngineView` 承载前端)
- **Frontend Stack:** React 19 + Tailwind CSS + Framer Motion (处理 60FPS 物理回弹)
- **State Management:** Zustand (轻量级，管理宠物状态与配置)
- **Backend Logic:** Python (负责 CPU/内存/网络采样、全局快捷键、文件持久化、剪贴板监听)

------

## 2. 核心功能实现细节

### 2.1 动画引擎与渲染逻辑

- **渲染模式:** 采用 `Canvas` 渲染像素序列帧，而非 `<img>` 标签，以减少高频切换导致的闪烁。

- **动态翻转:** 通过 CSS `transform: scaleX(-1)` 实现，由 Python 端计算 `target_x` 与 `current_x` 的差值触发。

- **物理效果:** 使用 `framer-motion` 的 `useSpring` 钩子处理拖拽：

  JavaScript

  ```
  const springConfig = { stiffness: 300, damping: 20 };
  // 当释放鼠标时，计算初始速度并触发回弹或滑动动画
  ```

### 2.2 透明异形窗口技术 (Transparent Window)

在 PySide6 主窗口中配置：

- `Qt.FramelessWindowHint`: 移除原生边框。
- `Qt.WindowStaysOnTopHint`: 窗口置顶。
- `Qt.WA_TranslucentBackground`: 开启背景透明。
- `Qt.WindowTransparentForInput`: 实现点击穿透（在宠物非像素点区域动态切换，防止干扰用户操作桌面文件）。
- **阴影处理:** 禁用 OS 级别阴影，改由 CSS `filter: drop-shadow` 手动绘制像素级阴影。

### 2.3 系统资源监控 (Python Side)

使用 Python 的 `psutil` 库进行数据采样：

- **采样周期:** 每 500ms 进行一次系统快照（通过 `QTimer` 触发）。
- **数据推送:** 通过 PySide6 `QWebEngineView` 的 `runJavaScript()` 或 `QWebChannel` 将 JSON 数据推送到前端。
- **网络计算:** 记录两次采样间的 `bytes_recv` / `bytes_sent` 差值，计算实时速率。

------

## 3. 数据持久化方案 (Data Persistence)

采用 Python 的 `appdirs` + `json` / `aiofiles` 实现轻量级本地存储：

- **存储路径:** `%APPDATA%/CyberZombie/settings.json`
- **保存内容:**
  - `coordinate`: `[x, y]` (最后一次退出的坐标)
  - `scaling`: `1.0 ~ 8.0` (当前缩放比例)
  - `memo_data`: `Array<{id, text, timestamp}>` (备忘录列表)
  - `evolution_points`: `int` (进化点/好感度数据)

------

## 4. 详细接口设计 (Inter-Process Communication)

### Python -> Frontend (Events)

| 事件名            | 数据结构                             | 触发时机           |
| ----------------- | ------------------------------------ | ------------------ |
| `sys_update`      | `{ cpu, mem, up, down }`             | 每 500ms 自动推送  |
| `clipboard_alert` | `{ content: string, type: "error" }` | 监测到关键词时推送 |
| `window_edge`     | `{ direction: "left"                 | "right" }`         |

### Frontend -> Python (Commands)

| 命令名              | 参数           | 功能说明                 |
| ------------------- | -------------- | ------------------------ |
| `save_memo`         | `data: String` | 将备忘录写入本地存储     |
| `set_always_on_top` | `state: bool`  | 切换置顶状态             |
| `set_click_through` | `state: bool`  | 设置鼠标是否穿透透明区域 |

------

## 5. UI/UX 设计规范 (Pixel Art Style)

### 5.1 视觉参数

- **调色盘:**
  - `Primary`: #00FF41 (矩阵绿，用于系统监控)
  - `Secondary`: #FF3131 (警报红，用于 Error 状态)
  - `Surface`: rgba(20, 20, 20, 0.8) (磨砂黑，用于 UI 面板)
- **字体:** 指定使用像素类字体（如 `Silver.ttf` 或 `Zpix.ttf`），禁用抗锯齿以保持硬核观感。

### 5.2 交互反馈

- **悬停逻辑 (2s Trigger):** 使用 `setTimeout` 计时，若 2s 内 `onMouseEnter` 且无 `onMouseLeave`，则在宠物上方平滑滑出 `MonitorPanel`。
- **备忘录动画:** 采用“像素展开”效果（Clip-path 动画），从宠物中心点向四周扩散。

------

## 6. 异常处理与性能优化

- **多显示器适配:** 使用 PySide6 的 `QGuiApplication.screens()` 获取逻辑分辨率，防止宠物“走”出屏幕区域。
- **GPU 加速:** 在 CSS 中使用 `will-change: transform` 强制开启 GPU 渲染，确保在 8 倍缩放时依然流畅。
- **低功耗模式:** 当全屏游戏或电脑进入休眠时，Python 端通过 `QTimer` 暂停采样线程。

------

## 7. 部署与安装

- **构建工具:** `PyInstaller` 或 `nuitka`（打包为单文件可执行程序）
- **目标平台:** Windows x64 / ARM64
- **体积:** 最终安装包预计 **< 50MB**（含 Python 运行时与 PySide6 库）。