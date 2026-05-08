import sys
import os

os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
os.environ["QT_SCALE_FACTOR"] = "1"

import json
import random

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import Qt, QTimer, QUrl, QPoint, QRect
from PySide6.QtGui import QCursor, QGuiApplication

import backend.storage as storage
from backend.monitor import SystemMonitor
from backend.clipboard_watcher import ClipboardWatcher
from backend.web_channel import WebBridge


class CyberZombieWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = storage.load()
        self.config = self.settings.get("config", {})

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.webview = QWebEngineView()
        self.webview.setContextMenuPolicy(Qt.NoContextMenu)
        self.webview.page().setBackgroundColor(Qt.transparent)

        self.base_w, self.base_h = 187, 471
        self.scale = max(0.2, min(8.0, self.config.get("scale", 1.0)))
        self.monitor_visible = False
        self.memo_visible = False
        self.panel_top_h = 150
        self.panel_bottom_h = 340
        self._resize_window()

        screen = self._total_geometry()
        default_x = screen.x() + screen.width() - self.width() - 20
        default_y = screen.y() + screen.height() - self.height() - 10
        pos = self.config.get("position", {"x": default_x, "y": default_y})
        self.move(pos["x"], pos["y"])

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.webview)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.channel = QWebChannel()
        self.monitor = SystemMonitor()
        self.bridge = WebBridge(storage, self.monitor)
        self.channel.registerObject("bridge", self.bridge)
        self.webview.page().setWebChannel(self.channel)

        frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "dist", "index.html")
        if os.path.exists(frontend_path):
            self.webview.setUrl(QUrl.fromLocalFile(os.path.abspath(frontend_path)))
        else:
            dev_path = os.path.join(os.path.dirname(__file__), "frontend", "index.html")
            self.webview.setUrl(QUrl.fromLocalFile(os.path.abspath(dev_path)))

        # 系统监控
        self.sys_timer = QTimer(self)
        self.sys_timer.timeout.connect(self._on_sys_tick)
        self.sys_timer.start(500)

        # 剪贴板
        self.clipboard = ClipboardWatcher()
        self.clipboard.alert.connect(self._on_clipboard_alert)
        self.clipboard.start()

        # 宠物状态
        self.pet_state = self.config.get("state", "IDLE")
        self.facing_right = True
        self.walk_speed = 3
        self.walk_timer = QTimer(self)
        self.walk_timer.timeout.connect(self._on_walk_tick)
        self.walk_timer.start(50)

        self.think_timer = QTimer(self)
        self.think_timer.timeout.connect(self._on_think_tick)
        self.think_timer.start(2000)

        # 拖拽
        self.drag_timer = QTimer(self)
        self.drag_timer.timeout.connect(self._on_drag_tick)
        self.dragging = False
        self.drag_start_pos = QPoint()
        self.drag_start_cursor = QPoint()
        self.velocity = [0, 0]

        # 惯性
        self.inertia_timer = QTimer(self)
        self.inertia_timer.timeout.connect(self._on_inertia_tick)
        self.inertia_velocity = [0, 0]

        # 贴边
        self.auto_hide = self.config.get("auto_hide", False)
        self.is_peeked = True
        self.hide_timer = QTimer(self)
        self.hide_timer.timeout.connect(self._on_hide_tick)
        self.peek_width = 24

        # 信号
        self.bridge.stateChanged.connect(self._on_state_changed)
        self.bridge.directionChanged.connect(self._on_direction_changed)
        self.bridge.scaleChanged.connect(self._on_scale_changed)
        self.bridge.dragStarted.connect(self._on_drag_started)
        self.bridge.dragEnded.connect(self._on_drag_ended)
        self.bridge.peekOutRequested.connect(self._on_peek_out)
        self.bridge.exitRequested.connect(self._on_exit)
        self.bridge.autoHideChanged.connect(self._on_auto_hide_changed)
        self.bridge.showMonitorChanged.connect(self._on_show_monitor_changed)
        self.bridge.panelLayoutChanged.connect(self._on_panel_layout_changed)

    def _resize_window(self):
        extra_top = self.panel_top_h if self.monitor_visible else 0
        extra_bottom = self.panel_bottom_h if self.memo_visible else 0
        min_w = 280 if self.memo_visible else int(self.base_w * self.scale)
        w = max(int(self.base_w * self.scale), min_w)
        h = int(self.base_h * self.scale) + extra_top + extra_bottom
        self.resize(w, h)

    @staticmethod
    def _total_geometry():
        screens = QGuiApplication.screens()
        if not screens:
            return QRect(0, 0, 1920, 1080)
        geo = screens[0].geometry()
        for s in screens[1:]:
            geo = geo.united(s.geometry())
        return geo

    def _on_sys_tick(self):
        if getattr(self.monitor, 'is_fullscreen_app_running', lambda: False)():
            return
        data = self.monitor.snapshot()
        self.bridge.emit_sys_update(data)

    def _on_clipboard_alert(self, data):
        self.bridge.emit_clipboard_alert(data)
        settings = storage.load()
        settings["stats"]["errors_caught"] = settings["stats"].get("errors_caught", 0) + 1
        storage.save(settings)

    def _on_state_changed(self, state):
        self.pet_state = state

    def _on_direction_changed(self, right):
        self.facing_right = right

    def _on_scale_changed(self, scale):
        self.scale = max(0.2, min(8.0, scale))
        old_extra_top = self.panel_top_h if self.monitor_visible else 0
        self._resize_window()
        new_extra_top = self.panel_top_h if self.monitor_visible else 0
        if new_extra_top != old_extra_top:
            self.move(self.x(), self.y() - (new_extra_top - old_extra_top))
        settings = storage.load()
        settings["config"]["scale"] = self.scale
        storage.save(settings)

    def _on_show_monitor_changed(self, state):
        pass

    def _on_panel_layout_changed(self, monitor_visible, memo_visible):
        old_top = self.panel_top_h if self.monitor_visible else 0
        old_w = self.width()
        self.monitor_visible = monitor_visible
        self.memo_visible = memo_visible
        new_top = self.panel_top_h if monitor_visible else 0
        new_bottom = self.panel_bottom_h if memo_visible else 0
        self._resize_window()
        w_delta = self.width() - old_w
        top_delta = new_top - old_top
        x = self.x()
        y = self.y()
        if w_delta > 0:
            geo = self._total_geometry()
            if x + self.width() > geo.x() + geo.width():
                x = max(geo.x(), geo.x() + geo.width() - self.width())
        if top_delta != 0:
            y -= top_delta
        if w_delta > 0 or top_delta != 0:
            self.move(x, y)

    def _on_think_tick(self):
        if self.dragging or self.pet_state == "PANIC":
            return
        if self.pet_state == "IDLE":
            if random.random() < 0.4:
                self._start_walking()
        elif self.pet_state == "WALK":
            if random.random() < 0.3:
                self.pet_state = "IDLE"
                self.bridge.stateChanged.emit("IDLE")

    def _start_walking(self):
        self.pet_state = "WALK"
        self.facing_right = random.choice([True, False])
        self.bridge.stateChanged.emit("WALK")
        self.bridge.directionChanged.emit(self.facing_right)

    def _on_walk_tick(self):
        if self.pet_state != "WALK" or self.dragging:
            return
        screen = self._total_geometry()
        if self.width() >= screen.width():
            return
        x = self.x()
        y = self.y()
        left = screen.x()
        right = screen.x() + screen.width() - self.width()
        if self.facing_right:
            x += self.walk_speed
            if x >= right:
                x = right
                self.facing_right = False
                self.bridge.emit_direction_changed(False)
        else:
            x -= self.walk_speed
            if x <= left:
                x = left
                self.facing_right = True
                self.bridge.emit_direction_changed(True)
        if random.random() < 0.1:
            y += random.choice([-1, 1]) * random.randint(1, 3)
            top = screen.y()
            bottom = screen.y() + screen.height() - self.height()
            y = max(top, min(y, bottom))
        self.move(x, y)

    def _on_drag_started(self):
        self.dragging = True
        self.drag_start_pos = self.pos()
        self.drag_start_cursor = QCursor.pos()
        self.walk_timer.stop()
        self.think_timer.stop()
        self.hide_timer.stop()
        self.inertia_timer.stop()
        self.drag_timer.start(16)

    def _on_drag_tick(self):
        if not self.dragging:
            self.drag_timer.stop()
            return
        delta = QCursor.pos() - self.drag_start_cursor
        new_pos = self.drag_start_pos + delta
        screen = self._total_geometry()
        x = max(screen.x(), min(new_pos.x(), screen.x() + screen.width() - self.width()))
        y = max(screen.y(), min(new_pos.y(), screen.y() + screen.height() - self.height()))
        self.velocity = [x - self.x(), y - self.y()]
        self.move(x, y)

    def _on_drag_ended(self):
        self.dragging = False
        self.drag_timer.stop()
        self._save_state()
        self.walk_timer.start(50)
        self.think_timer.start(2000)
        speed = (self.velocity[0] ** 2 + self.velocity[1] ** 2) ** 0.5
        if speed > 2:
            self.inertia_velocity = self.velocity.copy()
            self.inertia_timer.start(16)
        elif self.auto_hide and self.pet_state == "IDLE":
            self._start_hide_to_edge()

    def _on_inertia_tick(self):
        self.inertia_velocity[0] *= 0.92
        self.inertia_velocity[1] *= 0.92
        speed = (self.inertia_velocity[0] ** 2 + self.inertia_velocity[1] ** 2) ** 0.5
        if speed < 1:
            self.inertia_timer.stop()
            if self.auto_hide and self.pet_state == "IDLE":
                self._start_hide_to_edge()
            return
        screen = self._total_geometry()
        x = self.x() + self.inertia_velocity[0]
        y = self.y() + self.inertia_velocity[1]
        x = max(screen.x(), min(x, screen.x() + screen.width() - self.width()))
        y = max(screen.y(), min(y, screen.y() + screen.height() - self.height()))
        self.move(int(x), int(y))

    def _start_hide_to_edge(self):
        if not self.auto_hide or self.pet_state != "IDLE" or self.dragging:
            return
        self.hide_timer.start(16)

    def _on_hide_tick(self):
        screen = self._total_geometry()
        x = self.x()
        center = screen.x() + screen.width() // 2
        if x + self.width() // 2 < center:
            target_x = screen.x() - self.width() + self.peek_width
        else:
            target_x = screen.x() + screen.width() - self.peek_width
        if abs(x - target_x) < 4:
            self.move(int(target_x), self.y())
            self.hide_timer.stop()
            self.is_peeked = False
        else:
            step = 4 if target_x > x else -4
            self.move(x + step, self.y())

    def _on_peek_out(self):
        if self.is_peeked:
            return
        screen = self._total_geometry()
        x = self.x()
        if x < screen.x() + 10:
            target_x = screen.x() + 10
        else:
            target_x = screen.x() + screen.width() - self.width() - 10
        self.move(target_x, self.y())
        self.is_peeked = True
        self.hide_timer.stop()

    def _on_auto_hide_changed(self, state):
        self.auto_hide = state
        settings = storage.load()
        settings["config"]["auto_hide"] = state
        storage.save(settings)
        if not state and not self.is_peeked:
            self._on_peek_out()

    def _on_exit(self):
        self._save_state()
        self.clipboard.stop()
        self.walk_timer.stop()
        self.think_timer.stop()
        self.drag_timer.stop()
        self.inertia_timer.stop()
        self.hide_timer.stop()
        self.sys_timer.stop()
        QApplication.quit()

    def _save_state(self):
        geo = self._total_geometry()
        x = self.x()
        y = self.y()
        if x < geo.x() - self.width() + 8:
            x = geo.x() + geo.width() - self.width() - 20
        if y < geo.y():
            y = geo.y()
        elif y > geo.y() + geo.height() - 20:
            y = geo.y() + geo.height() - self.height() - 10
        settings = storage.load()
        settings["config"]["position"] = {"x": x, "y": y}
        settings["config"]["state"] = self.pet_state
        settings["config"]["scale"] = self.scale
        storage.save(settings)

    def closeEvent(self, event):
        self.clipboard.stop()
        self.walk_timer.stop()
        self.think_timer.stop()
        self.drag_timer.stop()
        self.inertia_timer.stop()
        self.hide_timer.stop()
        self.sys_timer.stop()
        self._save_state()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    window = CyberZombieWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
