import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw
from plumb.timer import TimerState
from plumb.database import db


class PlumbPreferencesWindow(Adw.PreferencesWindow):
    def __init__(self, timer=None, **kwargs):
        super().__init__(**kwargs)
        self.timer = timer
        self.set_title("Preferences")
        self.set_default_size(600, 700)

        timer_page = Adw.PreferencesPage(
            title="Timer", icon_name="document-open-recent-symbolic"
        )
        self.add(timer_page)

        session_group = Adw.PreferencesGroup(title="Session")
        timer_page.add(session_group)

        pomo_val = self.timer.durations[TimerState.FOCUS] if self.timer else 55
        self.pomo_row = self._create_spin_row(
            "Pomodoro Duration", "In minutes", 1, 90, pomo_val, self._on_pomo_changed
        )
        session_group.add(self.pomo_row)

        short_val = self.timer.durations[TimerState.SHORT_BREAK] if self.timer else 5
        self.short_break_row = self._create_spin_row(
            "Short Break Duration",
            "In minutes",
            1,
            30,
            short_val,
            self._on_short_break_changed,
        )
        session_group.add(self.short_break_row)

        long_val = (
            self.timer.durations.get(TimerState.LONG_BREAK, 10) if self.timer else 10
        )
        self.long_break_row = self._create_spin_row(
            "Long Break Duration",
            "In minutes",
            1,
            60,
            long_val,
            self._on_long_break_changed,
        )
        session_group.add(self.long_break_row)

        if hasattr(Adw, "SpinRow"):
            adj = Gtk.Adjustment(
                value=4,
                lower=1,
                upper=10,
                step_increment=1,
                page_increment=1,
                page_size=0,
            )
            self.cycles_row = Adw.SpinRow(title="Number of Cycles", adjustment=adj)
        else:
            self.cycles_row = Adw.ActionRow(title="Number of Cycles")
            self.cycles_spin = Gtk.SpinButton.new_with_range(1, 10, 1)
            self.cycles_spin.set_valign(Gtk.Align.CENTER)
            self.cycles_spin.set_value(4)
            self.cycles_row.add_suffix(self.cycles_spin)

        session_group.add(self.cycles_row)

        self.summary_label = Gtk.Label()
        self.summary_label.set_markup(
            "A single session will take <b>4 hours 5 minutes</b>.\n<b>10%</b> of the time will be allocated for breaks."
        )
        self.summary_label.set_halign(Gtk.Align.START)
        self.summary_label.set_margin_top(16)
        self.summary_label.set_margin_bottom(16)
        self.summary_label.add_css_class("dim-label")
        session_group.add(self.summary_label)

        behavior_group = Adw.PreferencesGroup(title="Behavior")
        timer_page.add(behavior_group)

        self.pause_lock_row = Adw.ActionRow(title="Pause By Locking The Screen")
        self.pause_lock_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.pause_lock_switch.set_active(
            self.timer.pause_on_lock if self.timer else True
        )
        self.pause_lock_switch.connect("notify::active", self._on_pause_lock_changed)
        self.pause_lock_row.add_suffix(self.pause_lock_switch)
        behavior_group.add(self.pause_lock_row)

        self.confirm_break_row = Adw.ActionRow(title="Confirm Starting a Break")
        self.confirm_break_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.confirm_break_switch.set_active(
            not self.timer.auto_start_breaks if self.timer else True
        )
        self.confirm_break_switch.connect(
            "notify::active", self._on_confirm_break_changed
        )
        self.confirm_break_row.add_suffix(self.confirm_break_switch)
        behavior_group.add(self.confirm_break_row)

        self.confirm_pomo_row = Adw.ActionRow(title="Confirm Starting a Pomodoro")
        self.confirm_pomo_switch = Gtk.Switch(valign=Gtk.Align.CENTER)
        self.confirm_pomo_switch.set_active(
            not self.timer.auto_start_pomodoros if self.timer else True
        )
        self.confirm_pomo_switch.connect(
            "notify::active", self._on_confirm_pomo_changed
        )
        self.confirm_pomo_row.add_suffix(self.confirm_pomo_switch)
        behavior_group.add(self.confirm_pomo_row)

        notif_page = Adw.PreferencesPage(
            title="Notifications", icon_name="preferences-system-notifications-symbolic"
        )

        ann_group = Adw.PreferencesGroup(title="Announcements")
        self.notify_row = Adw.ActionRow(
            title="Time Running Out",
            subtitle="Notify when Pomodoro or break is about to end.",
        )
        self.notify_switch = Gtk.Switch(
            active=self.timer.notify_running_out if self.timer else True,
            valign=Gtk.Align.CENTER,
        )
        self.notify_switch.connect(
            "notify::active", self._on_notify_running_out_changed
        )
        self.notify_row.add_suffix(self.notify_switch)
        ann_group.add(self.notify_row)

        self.dnd_row = Adw.ActionRow(
            title="System Do Not Disturb",
            subtitle="Automatically mute system notifications during a focus session.",
        )
        self.dnd_switch = Gtk.Switch(
            active=self.timer.dnd_sync if self.timer else False, valign=Gtk.Align.CENTER
        )
        self.dnd_switch.connect("notify::active", self._on_dnd_sync_changed)
        self.dnd_row.add_suffix(self.dnd_switch)
        ann_group.add(self.dnd_row)

        notif_page.add(ann_group)

        overlay_group = Adw.PreferencesGroup(
            title="Screen Overlay",
            description="A full-screen notification intended to enforce taking a break.",
        )

        self.overlay_row = Adw.ActionRow(title="Screen Overlay")
        self.overlay_switch = Gtk.Switch(
            active=self.timer.enable_screen_overlay if self.timer else False,
            valign=Gtk.Align.CENTER,
        )
        self.overlay_switch.connect("notify::active", self._on_overlay_changed)
        self.overlay_row.add_suffix(self.overlay_switch)
        overlay_group.add(self.overlay_row)

        self.quotes_row = Adw.ActionRow(
            title="Show Fun Quotes",
            subtitle="Display a random quote at the bottom of the screen overlay.",
        )
        self.quotes_switch = Gtk.Switch(
            active=self.timer.show_overlay_quotes if self.timer else True,
            valign=Gtk.Align.CENTER,
        )
        self.quotes_switch.connect("notify::active", self._on_quotes_changed)
        self.quotes_row.add_suffix(self.quotes_switch)
        overlay_group.add(self.quotes_row)

        self.lock_row = Adw.ComboRow(
            title="Lock Delay", subtitle="Period of inactivity to lock the screen."
        )
        self.lock_model = Gtk.StringList.new(["Never", "1 minute", "5 minutes"])
        self.lock_row.set_model(self.lock_model)
        self._set_combo_selected_string(
            self.lock_row,
            self.lock_model,
            self.timer.lock_delay if self.timer else "Never",
        )
        self.lock_row.connect("notify::selected-item", self._on_lock_delay_changed)
        overlay_group.add(self.lock_row)

        self.reopen_row = Adw.ComboRow(
            title="Reopen Delay",
            subtitle="Period of inactivity to reopen the overlay after it gets dismissed.",
        )
        self.reopen_model = Gtk.StringList.new(["30 seconds", "1 minute", "5 minutes"])
        self.reopen_row.set_model(self.reopen_model)
        self._set_combo_selected_string(
            self.reopen_row,
            self.reopen_model,
            self.timer.reopen_delay if self.timer else "30 seconds",
        )
        self.reopen_row.connect("notify::selected-item", self._on_reopen_delay_changed)
        overlay_group.add(self.reopen_row)

        notif_page.add(overlay_group)
        self.add(notif_page)

    def _create_spin_row(
        self, title_text, subtitle_text, min_val, max_val, default_val, callback
    ):
        if hasattr(Adw, "SpinRow"):
            adj = Gtk.Adjustment(
                value=default_val,
                lower=min_val,
                upper=max_val,
                step_increment=1,
                page_increment=1,
                page_size=0,
            )
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
        if not self.timer:
            return
        if value == self.timer.durations.get(state, 0):
            return

        if self.timer.is_running and self.timer.state == state:
            self.timer.set_duration(state, value, update_active=False)
            toast = Adw.Toast.new("Changes will apply to the next session")
            self.add_toast(toast)
        else:
            self.timer.set_duration(state, value)

    def _on_pomo_changed(self, value):
        self._handle_duration_change(
            TimerState.FOCUS, value, getattr(self, "pomo_row", None)
        )

    def _on_short_break_changed(self, value):
        self._handle_duration_change(
            TimerState.SHORT_BREAK, value, getattr(self, "short_break_row", None)
        )

    def _on_long_break_changed(self, value):
        self._handle_duration_change(
            TimerState.LONG_BREAK, value, getattr(self, "long_break_row", None)
        )

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

    def _set_combo_selected_string(self, combo, model, target_string):
        for i in range(model.get_n_items()):
            if model.get_string(i) == target_string:
                combo.set_selected(i)
                return

    def _on_notify_running_out_changed(self, switch, param):
        if self.timer:
            self.timer.notify_running_out = switch.get_active()
            db.set_setting("notify_running_out", str(self.timer.notify_running_out))

    def _on_dnd_sync_changed(self, switch, param):
        if self.timer:
            self.timer.dnd_sync = switch.get_active()
            db.set_setting("dnd_sync", str(self.timer.dnd_sync))

            if self.timer.is_running and self.timer.state == TimerState.FOCUS:
                self.timer._set_gnome_dnd(self.timer.dnd_sync)

    def _on_overlay_changed(self, switch, param):
        if self.timer:
            self.timer.enable_screen_overlay = switch.get_active()
            db.set_setting(
                "enable_screen_overlay", str(self.timer.enable_screen_overlay)
            )

    def _on_quotes_changed(self, switch, param):
        if self.timer:
            self.timer.show_overlay_quotes = switch.get_active()
            db.set_setting("show_overlay_quotes", str(self.timer.show_overlay_quotes))

    def _on_lock_delay_changed(self, combo, param):
        if self.timer:
            selected_str = self.lock_model.get_string(combo.get_selected())
            self.timer.lock_delay = selected_str
            db.set_setting("lock_delay", selected_str)

    def _on_reopen_delay_changed(self, combo, param):
        if self.timer:
            selected_str = self.reopen_model.get_string(combo.get_selected())
            self.timer.reopen_delay = selected_str
            db.set_setting("reopen_delay", selected_str)
