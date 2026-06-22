import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw
from tapas.timer import TimerState
from tapas.database import db

class TapasPreferencesWindow(Adw.PreferencesWindow):
    def __init__(self, timer=None, **kwargs):
        super().__init__(**kwargs)
        self.timer = timer
        self.set_title("Preferences")
        self.set_default_size(600, 700)
        
        timer_page = Adw.PreferencesPage(title="Timer", icon_name="document-open-recent-symbolic")
        self.add(timer_page)
        
        session_group = Adw.PreferencesGroup(title="Session")
        timer_page.add(session_group)
        
        pomo_val = self.timer.durations[TimerState.FOCUS] if self.timer else 55
        self.pomo_row = self._create_spin_row("Pomodoro Duration", "In minutes", 1, 90, pomo_val, self._on_pomo_changed)
        session_group.add(self.pomo_row)
        
        short_val = self.timer.durations[TimerState.SHORT_BREAK] if self.timer else 5
        self.short_break_row = self._create_spin_row("Short Break Duration", "In minutes", 1, 30, short_val, self._on_short_break_changed)
        session_group.add(self.short_break_row)
        
        long_val = self.timer.durations.get(TimerState.LONG_BREAK, 10) if self.timer else 10
        self.long_break_row = self._create_spin_row("Long Break Duration", "In minutes", 1, 60, long_val, self._on_long_break_changed)
        session_group.add(self.long_break_row)
        
        if hasattr(Adw, "SpinRow"):
            adj = Gtk.Adjustment(value=4, lower=1, upper=10, step_increment=1, page_increment=1, page_size=0)
            self.cycles_row = Adw.SpinRow(title="Number of Cycles", adjustment=adj)
        else:
            self.cycles_row = Adw.ActionRow(title="Number of Cycles")
            self.cycles_spin = Gtk.SpinButton.new_with_range(1, 10, 1)
            self.cycles_spin.set_valign(Gtk.Align.CENTER)
            self.cycles_spin.set_value(4)
            self.cycles_row.add_suffix(self.cycles_spin)
            
        session_group.add(self.cycles_row)
        
        self.summary_label = Gtk.Label()
        self.summary_label.set_markup("A single session will take <b>4 hours 5 minutes</b>.\n<b>10%</b> of the time will be allocated for breaks.")
        self.summary_label.set_halign(Gtk.Align.START)
        self.summary_label.set_margin_top(16)
        self.summary_label.set_margin_bottom(16)
        self.summary_label.add_css_class("dim-label")
        session_group.add(self.summary_label)

        behavior_group = Adw.PreferencesGroup(title="Behavior")
        timer_page.add(behavior_group)
        
        self.pause_lock_row = Adw.ActionRow(title="Pause By Locking The Screen")
        self.pause_lock_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.pause_lock_switch.set_active(self.timer.pause_on_lock if self.timer else True)
        self.pause_lock_switch.connect("notify::active", self._on_pause_lock_changed)
        self.pause_lock_row.add_suffix(self.pause_lock_switch)
        behavior_group.add(self.pause_lock_row)
        
        self.confirm_break_row = Adw.ActionRow(title="Confirm Starting a Break")
        self.confirm_break_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.confirm_break_switch.set_active(not self.timer.auto_start_breaks if self.timer else True)
        self.confirm_break_switch.connect("notify::active", self._on_confirm_break_changed)
        self.confirm_break_row.add_suffix(self.confirm_break_switch)
        behavior_group.add(self.confirm_break_row)
        
        self.confirm_pomo_row = Adw.ActionRow(title="Confirm Starting a Pomodoro")
        self.confirm_pomo_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.confirm_pomo_switch.set_active(not self.timer.auto_start_pomodoros if self.timer else True)
        self.confirm_pomo_switch.connect("notify::active", self._on_confirm_pomo_changed)
        self.confirm_pomo_row.add_suffix(self.confirm_pomo_switch)
        behavior_group.add(self.confirm_pomo_row)
        
        self.add(Adw.PreferencesPage(title="Notifications", icon_name="appointment-soon-symbolic"))
        self.add(Adw.PreferencesPage(title="Sounds", icon_name="audio-volume-high-symbolic"))
        self.add(Adw.PreferencesPage(title="Appearance", icon_name="applications-graphics-symbolic"))
        self.add(Adw.PreferencesPage(title="Keyboard Shortcuts", icon_name="input-keyboard-symbolic"))
        self.add(Adw.PreferencesPage(title="Integrations", icon_name="preferences-system-symbolic"))

    def _create_spin_row(self, title_text, subtitle_text, min_val, max_val, default_val, callback):
        if hasattr(Adw, "SpinRow"):
            adj = Gtk.Adjustment(value=default_val, lower=min_val, upper=max_val, step_increment=1, page_increment=1, page_size=0)
            row = Adw.SpinRow(title=title_text, subtitle=subtitle_text, adjustment=adj)
            row.adj = adj
            row.connect("notify::value", lambda r, p: callback(int(r.get_value())))
            return row
        else:
            row = Adw.ActionRow(title=title_text, subtitle=subtitle_text)
            spin = Gtk.SpinButton.new_with_range(min_val, max_val, 1)
            spin.set_value(default_val)
            spin.set_valign(Gtk.Align.CENTER)
            spin.connect("value-changed", lambda s: callback(int(s.get_value())))
            row.add_suffix(spin)
            return row

    def _handle_duration_change(self, state, value, row_ref):
        if not self.timer: return
        if value == self.timer.durations.get(state, 0): return

        if self.timer.is_running and self.timer.state == state:
            self.timer.set_duration(state, value, update_active=False)
            toast = Adw.Toast.new("Changes will apply to the next session")
            self.add_toast(toast)
        else:
            self.timer.set_duration(state, value)

    def _on_pomo_changed(self, value):
        self._handle_duration_change(TimerState.FOCUS, value, getattr(self, 'pomo_row', None))

    def _on_short_break_changed(self, value):
        self._handle_duration_change(TimerState.SHORT_BREAK, value, getattr(self, 'short_break_row', None))

    def _on_long_break_changed(self, value):
        self._handle_duration_change(TimerState.LONG_BREAK, value, getattr(self, 'long_break_row', None))

    def _on_pause_lock_changed(self, switch, param):
        if self.timer:
            self.timer.pause_on_lock = switch.get_active()
            db.set_setting("pause_on_lock", str(self.timer.pause_on_lock))
            
    def _on_confirm_break_changed(self, switch, param):
        if self.timer:
            self.timer.auto_start_breaks = not switch.get_active()
            db.set_setting("auto_start_breaks", str(self.timer.auto_start_breaks))
            
    def _on_confirm_pomo_changed(self, switch, param):
        if self.timer:
            self.timer.auto_start_pomodoros = not switch.get_active()
            db.set_setting("auto_start_pomodoros", str(self.timer.auto_start_pomodoros))
