import gi
gi.require_version('GLib', '2.0')
from gi.repository import GLib
from tapas.database import db

class TimerState:
    FOCUS = "Focus"
    SHORT_BREAK = "Short Break"
    LONG_BREAK = "Long Break"

class TimerLogic:
    def __init__(self):
        self.state = TimerState.FOCUS
        self.is_running = False
        
        # Default durations (in minutes)
        self.durations = {
            TimerState.FOCUS: int(db.get_setting("duration_focus", 25)),
            TimerState.SHORT_BREAK: int(db.get_setting("duration_short_break", 5)),
            TimerState.LONG_BREAK: int(db.get_setting("duration_long_break", 15))
        }
        
        self.time_left = self.durations[self.state] * 60
        self.current_total_time = self.time_left
        self.focus_sessions_completed = 0
        
        self.auto_start_breaks = db.get_setting("auto_start_breaks", "False") == "True"
        self.auto_start_pomodoros = db.get_setting("auto_start_pomodoros", "False") == "True"
        self.pause_on_lock = db.get_setting("pause_on_lock", "True") == "True"
        
        # Callbacks that the UI can hook into
        self.on_tick_callback = None
        self.on_finish_callback = None
        self.on_state_change_callback = None
        self.on_warning_callback = None
        self.on_run_state_change_callback = None
        
        self._timeout_id = None

    def set_duration(self, state, duration_minutes, update_active=True):
        old_duration = self.durations.get(state, 0)
        self.durations[state] = duration_minutes
        
        if state == TimerState.FOCUS: db.set_setting("duration_focus", duration_minutes)
        elif state == TimerState.SHORT_BREAK: db.set_setting("duration_short_break", duration_minutes)
        elif state == TimerState.LONG_BREAK: db.set_setting("duration_long_break", duration_minutes)
        
        if self.state == state and update_active:
            delta_minutes = duration_minutes - old_duration
            self.time_left += delta_minutes * 60
            self.current_total_time = duration_minutes * 60
            if self.time_left < 0:
                self.time_left = 0
                
            if self.on_tick_callback:
                self.on_tick_callback(self.time_left)

    def start(self):
        if not self.is_running:
            self.is_running = True
            if self.on_run_state_change_callback:
                self.on_run_state_change_callback(True)
            self._timeout_id = GLib.timeout_add(1000, self._on_tick)

    def pause(self):
        if self.is_running:
            self.is_running = False
            if self.on_run_state_change_callback:
                self.on_run_state_change_callback(False)
            if self._timeout_id:
                GLib.source_remove(self._timeout_id)
                self._timeout_id = None

    def reset(self):
        self.pause()
        self.time_left = self.durations[self.state] * 60
        self.current_total_time = self.time_left
        if self.on_tick_callback:
            self.on_tick_callback(self.time_left)

    def next_state(self):
        """Automatically transitions to the next Pomodoro state."""
        if self.state == TimerState.FOCUS:
            self.focus_sessions_completed += 1
            if self.focus_sessions_completed % 4 == 0:
                self.state = TimerState.LONG_BREAK
            else:
                self.state = TimerState.SHORT_BREAK
        else:
            self.state = TimerState.FOCUS
            
        self.time_left = self.durations[self.state] * 60
        self.current_total_time = self.time_left
        
        if self.on_state_change_callback:
            self.on_state_change_callback(self.state)

    def _on_tick(self):
        if not self.is_running:
            return GLib.SOURCE_REMOVE

        if self.time_left > 0:
            self.time_left -= 1
            if self.time_left == 10 and self.on_warning_callback:
                self.on_warning_callback()
            if self.on_tick_callback:
                self.on_tick_callback(self.time_left)
            return GLib.SOURCE_CONTINUE
            
        # Timer hit 0
        completed_state = self.state
        completed_duration = self.durations[self.state]
        
        self.is_running = False
        self.next_state() # Automatically prep the next state
        
        if self.state == TimerState.FOCUS and self.auto_start_pomodoros:
            self.start()
        elif self.state != TimerState.FOCUS and self.auto_start_breaks:
            self.start()
        
        if self.on_finish_callback:
            self.on_finish_callback(completed_state, completed_duration)
            
        return GLib.SOURCE_REMOVE

class StopwatchLogic:
    def __init__(self):
        self.elapsed_seconds = 0
        self.is_running = False
        self.on_tick_callback = None
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

    def reset(self):
        self.pause()
        self.elapsed_seconds = 0
        if self.on_tick_callback:
            self.on_tick_callback(self.elapsed_seconds)

    def _on_tick(self):
        if not self.is_running:
            return GLib.SOURCE_REMOVE

        self.elapsed_seconds += 1
        if self.on_tick_callback:
            self.on_tick_callback(self.elapsed_seconds)
        return GLib.SOURCE_CONTINUE
