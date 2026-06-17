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
        self.set_default_size(600, 700)
        
        timer_page = Adw.PreferencesPage(title="Timer", icon_name="document-open-recent-symbolic")
        self.add(timer_page)
        
        session_group = Adw.PreferencesGroup(title="Session")
        timer_page.add(session_group)
        
        pomo_val = self.timer.durations[TimerState.FOCUS] if self.timer else 55
        self.pomo_row = self._create_slider_row("Pomodoro Duration", 1, 90, pomo_val)
        self.pomo_row.scale.connect("value-changed", self._on_pomo_changed)
        session_group.add(self.pomo_row)
        
        short_val = self.timer.durations[TimerState.SHORT_BREAK] if self.timer else 5
        self.short_break_row = self._create_slider_row("Short Break Duration", 1, 30, short_val)
        self.short_break_row.scale.connect("value-changed", self._on_short_break_changed)
        session_group.add(self.short_break_row)
        
        long_val = self.timer.durations.get(TimerState.LONG_BREAK, 10) if self.timer else 10
        self.long_break_row = self._create_slider_row("Long Break Duration", 1, 60, long_val)
        self.long_break_row.scale.connect("value-changed", self._on_long_break_changed)
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
        self.pause_lock_switch.set_active(True)
        self.pause_lock_row.add_suffix(self.pause_lock_switch)
        behavior_group.add(self.pause_lock_row)
        
        self.confirm_break_row = Adw.ActionRow(title="Confirm Starting a Break")
        self.confirm_break_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.confirm_break_switch.set_active(True)
        self.confirm_break_row.add_suffix(self.confirm_break_switch)
        behavior_group.add(self.confirm_break_row)
        
        self.confirm_pomo_row = Adw.ActionRow(title="Confirm Starting a Pomodoro")
        self.confirm_pomo_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.confirm_pomo_switch.set_active(True)
        self.confirm_pomo_row.add_suffix(self.confirm_pomo_switch)
        behavior_group.add(self.confirm_pomo_row)
        
        self.add(Adw.PreferencesPage(title="Notifications", icon_name="appointment-soon-symbolic"))
        self.add(Adw.PreferencesPage(title="Sounds", icon_name="audio-volume-high-symbolic"))
        self.add(Adw.PreferencesPage(title="Appearance", icon_name="applications-graphics-symbolic"))
        self.add(Adw.PreferencesPage(title="Keyboard Shortcuts", icon_name="input-keyboard-symbolic"))
        self.add(Adw.PreferencesPage(title="Integrations", icon_name="preferences-system-symbolic"))

    def _create_slider_row(self, title_text, min_val, max_val, default_val):
        row = Adw.PreferencesRow()
        row.set_selectable(False)
        
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)
        vbox.set_margin_start(16)
        vbox.set_margin_end(16)
        
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title = Gtk.Label(label=title_text, halign=Gtk.Align.START, hexpand=True)
        value = Gtk.Label(label=f"{default_val} minutes")
        hbox.append(title)
        hbox.append(value)
        
        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, min_val, max_val, 1)
        scale.set_value(default_val)
        scale.set_hexpand(True)
        scale.set_draw_value(False)
        
        def on_scale_changed(s):
            val = int(s.get_value())
            value.set_label(f"{val} minutes")
            
        scale.connect("value-changed", on_scale_changed)
        
        vbox.append(hbox)
        vbox.append(scale)
        row.set_child(vbox)
        
        row.scale = scale 
        return row

    def _on_pomo_changed(self, scale):
        if self.timer:
            self.timer.set_duration(TimerState.FOCUS, int(scale.get_value()))

    def _on_short_break_changed(self, scale):
        if self.timer:
            self.timer.set_duration(TimerState.SHORT_BREAK, int(scale.get_value()))

    def _on_long_break_changed(self, scale):
        if self.timer:
            self.timer.set_duration(TimerState.LONG_BREAK, int(scale.get_value()))
