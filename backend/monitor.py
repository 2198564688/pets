import psutil
import time
import ctypes
from ctypes import wintypes

class SystemMonitor:
    def __init__(self):
        self.last_net = psutil.net_io_counters()
        self.last_time = time.time()

    def snapshot(self):
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().percent

        net = psutil.net_io_counters()
        now = time.time()
        dt = max(now - self.last_time, 0.001)

        up = max(0, (net.bytes_sent - self.last_net.bytes_sent) / dt / 1024)
        down = max(0, (net.bytes_recv - self.last_net.bytes_recv) / dt / 1024)

        self.last_net = net
        self.last_time = now

        return {
            "cpu": round(cpu, 1),
            "mem": round(mem, 1),
            "up": round(up, 1),
            "down": round(down, 1)
        }

    def is_fullscreen_app_running(self):
        """检测前台窗口是否全屏（Windows 专用）"""
        try:
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return False
            rect = wintypes.RECT()
            user32.GetWindowRect(hwnd, ctypes.byref(rect))
            # 获取主屏幕分辨率
            hdc = user32.GetDC(0)
            gdi32 = ctypes.windll.gdi32
            screen_w = gdi32.GetDeviceCaps(hdc, 118)  # HORZRES
            screen_h = gdi32.GetDeviceCaps(hdc, 117)  # VERTRES
            user32.ReleaseDC(0, hdc)
            w = rect.right - rect.left
            h = rect.bottom - rect.top
            return w >= screen_w - 10 and h >= screen_h - 10
        except Exception:
            return False
