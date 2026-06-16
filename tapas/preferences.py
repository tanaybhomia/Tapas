import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
from tapas.timer import TimerState

class TapasPreferencesWindow(Adw.PreferencesWindow):
    def __init__(self, timer=None, **kwargs):
        super().__init__(**kwargs)
        self.timer = timer
        self.set_title("Preferences")
        self.set_default_size(400, 500)
        
        # General Page
        page = Adw.PreferencesPage(title="General", icon_name="settings-configure-symbolic")
        self.add(page)
        
        # Timer Group
        timer_group = Adw.PreferencesGroup(title="Timer Settings", description="Customize your focus sessions")
        page.add(timer_group)
        
        # Pomodoro Duration Row
        self.pomodoro_spin = Gtk.SpinButton.new_with_range(1, 60, 1)
        val = self.timer.durations[TimerState.FOCUS] if self.timer else 25
        self.pomodoro_spin.set_value(val)
        self.pomodoro_spin.set_valign(Gtk.Align.CENTER)
        self.pomodoro_spin.connect("value-changed", self._on_pomo_changed)
        
        pomo_row = Adw.ActionRow(title="Pomodoro Duration", subtitle="In minutes")
        pomo_row.add_suffix(self.pomodoro_spin)
        timer_group.add(pomo_row)
        
        # Break Duration Row
        self.break_spin = Gtk.SpinButton.new_with_range(1, 30, 1)
        val = self.timer.durations[TimerState.SHORT_BREAK] if self.timer else 5
        self.break_spin.set_value(val)
        self.break_spin.set_valign(Gtk.Align.CENTER)
        self.break_spin.connect("value-changed", self._on_break_changed)
        
        break_row = Adw.ActionRow(title="Short Break Duration", subtitle="In minutes")
        break_row.add_suffix(self.break_spin)
        timer_group.add(break_row)

    def _on_pomo_changed(self, spin):
        if self.timer:
            self.timer.durations[TimerState.FOCUS] = int(spin.get_value())
            # If the user is currently on the Focus phase and stopped, update immediately
            if not self.timer.is_running and self.timer.state == TimerState.FOCUS:
                self.timer.reset()
                
    def _on_break_changed(self, spin):
        if self.timer:
            self.timer.durations[TimerState.SHORT_BREAK] = int(spin.get_value())
            # If the user is currently on the Break phase and stopped, update immediately
            if not self.timer.is_running and self.timer.state == TimerState.SHORT_BREAK:
                self.timer.reset()
