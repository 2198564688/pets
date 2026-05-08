from PySide6.QtCore import QTimer, QObject, Signal

try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False


class ClipboardWatcher(QObject):
    alert = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.last_text = ""
        self.keywords = [
            "error", "exception", "traceback", "bug", "fail", "panic",
            "fatal", "crash", "segfault", "null", "undefined",
        ]
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._poll)
        self._active = False

    def start(self):
        if not HAS_PYPERCLIP:
            return
        self._active = True
        self._timer.start(500)

    def stop(self):
        self._active = False
        self._timer.stop()

    def _poll(self):
        if not self._active or not HAS_PYPERCLIP:
            return
        try:
            text = pyperclip.paste()
        except Exception:
            return
        if not text or text == self.last_text:
            return
        self.last_text = text
        lower = text.lower()
        if any(k in lower for k in self.keywords):
            snippet = text[:300].replace('\n', ' ')
            self.alert.emit({"content": snippet, "type": "error"})
