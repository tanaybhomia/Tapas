import gi
gi.require_version('GLib', '2.0')
from gi.repository import GLib

class TimerState:
    FOCUS = "focus"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"

class TimerLogic:
    def __init__(self):
        self.state = TimerState.FOCUS
        self.is_running = False
        self.time_left = 25 * 60  # Default 25 minutes
        
        # Callbacks that the UI can hook into
        self.on_tick_callback = None
        self.on_finish_callback = None
        
        self._timeout_id = None

    def start(self):
        if not self.is_running:
            self.is_running = True
            self._timeout_id = GLib.timeout_add(1000, self._on_tick)

    def pause(self):
        if self.is_running:
            self.is_running = False
            if self._timeout_id:
                GLib.source_remove(self._timeout_id)
                self._timeout_id = None

    def reset(self, minutes: int):
        self.pause()
        self.time_left = minutes * 60
        if self.on_tick_callback:
            self.on_tick_callback(self.time_left)

    def _on_tick(self):
        if not self.is_running:
            return GLib.SOURCE_REMOVE

        if self.time_left > 0:
            self.time_left -= 1
            if self.on_tick_callback:
                self.on_tick_callback(self.time_left)
            return GLib.SOURCE_CONTINUE
            
        self.is_running = False
        if self.on_finish_callback:
            self.on_finish_callback()
            
        return GLib.SOURCE_REMOVE
