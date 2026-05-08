from PySide6.QtCore import QObject, Slot, Signal

class WebBridge(QObject):
    # 定义前端可监听的事件
    sysUpdate = Signal(dict)
    clipboardAlert = Signal(dict)
    windowEdge = Signal(dict)
    directionChanged = Signal(bool)   # True=right, False=left
    stateChanged = Signal(str)
    scaleChanged = Signal(float)
    clickThroughChanged = Signal(bool)
    dragStarted = Signal()
    dragEnded = Signal()
    peekOutRequested = Signal()
    exitRequested = Signal()
    autoHideChanged = Signal(bool)
    showMonitorChanged = Signal(bool)
    panelLayoutChanged = Signal(bool, bool)

    def __init__(self, storage, monitor):
        super().__init__()
        self.storage = storage
        self.monitor = monitor

    @Slot(float, result=str)
    def setScale(self, scale):
        self.scaleChanged.emit(scale)
        return "ok"

    @Slot()
    def startDrag(self):
        self.dragStarted.emit()

    @Slot()
    def endDrag(self):
        self.dragEnded.emit()

    @Slot()
    def peekOut(self):
        self.peekOutRequested.emit()

    @Slot()
    def exitApp(self):
        self.exitRequested.emit()

    @Slot(bool, result=str)
    def setAutoHide(self, state):
        self.autoHideChanged.emit(state)
        return "ok"

    @Slot(bool, result=str)
    def setShowMonitor(self, state):
        self.showMonitorChanged.emit(state)
        return "ok"

    @Slot(bool, bool, result=str)
    def setPanelLayout(self, monitorVisible, memoVisible):
        self.panelLayoutChanged.emit(monitorVisible, memoVisible)
        return "ok"

    @Slot(str, result=str)
    def saveMemo(self, data):
        try:
            import json
            memo_data = json.loads(data)
            settings = self.storage.load()
            settings["memos"] = memo_data
            self.storage.save(settings)
            return json.dumps({"ok": True})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

    @Slot(bool, result=str)
    def setAlwaysOnTop(self, state):
        # 由主窗口处理
        return "ok"

    @Slot(bool, result=str)
    def setClickThrough(self, state):
        self.clickThroughChanged.emit(state)
        return "ok"

    @Slot(str, result=str)
    def setPetState(self, state):
        self.stateChanged.emit(state)
        return "ok"

    @Slot(result=str)
    def loadSettings(self):
        import json
        return json.dumps(self.storage.load())

    @Slot(str, result=str)
    def saveConfig(self, config_json):
        try:
            import json
            config = json.loads(config_json)
            settings = self.storage.load()
            settings["config"].update(config)
            self.storage.save(settings)
            return json.dumps({"ok": True})
        except Exception as e:
            return json.dumps({"ok": False, "error": str(e)})

    def emit_sys_update(self, data):
        self.sysUpdate.emit(data)

    def emit_clipboard_alert(self, data):
        self.clipboardAlert.emit(data)

    def emit_direction_changed(self, right):
        self.directionChanged.emit(right)
