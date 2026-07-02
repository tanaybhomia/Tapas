import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio
from plumb.window import PlumbWindow


class PlumbApplication(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="com.github.tanay.Plumb",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
        )
        self._setup_actions()

    def _setup_actions(self):
        prefs_action = Gio.SimpleAction.new("preferences", None)
        prefs_action.connect("activate", self._on_preferences_action)
        self.add_action(prefs_action)
        self.set_accels_for_action("app.preferences", ["<Primary>comma"])

        take_break_action = Gio.SimpleAction.new("take-break", None)
        take_break_action.connect("activate", self._on_take_break)
        self.add_action(take_break_action)

        skip_break_action = Gio.SimpleAction.new("skip-break", None)
        skip_break_action.connect("activate", self._on_skip_break)
        self.add_action(skip_break_action)
        
        start_pomo_action = Gio.SimpleAction.new("start-pomodoro", None)
        start_pomo_action.connect("activate", self._on_start_pomodoro)
        self.add_action(start_pomo_action)

        skip_pomo_action = Gio.SimpleAction.new("skip-pomodoro", None)
        skip_pomo_action.connect("activate", self._on_skip_pomodoro)
        self.add_action(skip_pomo_action)

        toggle_compact_action = Gio.SimpleAction.new("toggle-compact", None)
        toggle_compact_action.connect("activate", self._on_toggle_compact)
        self.add_action(toggle_compact_action)
        self.set_accels_for_action("app.toggle-compact", ["<Alt>c"])

        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self._on_quit_action)
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Primary>q"])

    def _do_quit(self):
        import sys

        win = self.props.active_window
        if (
            win
            and hasattr(win, "timer")
            and win.timer
            and getattr(win.timer, "dnd_sync", False)
        ):
            win.timer._set_gnome_dnd(False)
        self.quit()
        sys.exit(0)

    def _attempt_quit(self, win):
        if not win or not hasattr(win, "timer"):
            self._do_quit()
            return

        is_pomodoro_active = win.timer.is_running or win.timer.time_left < (win.timer.durations.get(win.timer.state, 0) * 60)
        is_stopwatch_active = win.stopwatch.is_running or win.stopwatch.elapsed_seconds > 0

        if is_pomodoro_active or is_stopwatch_active:
            dialog = Adw.MessageDialog(
                heading="Active Session in Progress",
            )
            dialog.set_transient_for(win)
            
            dialog.add_response("cancel", "Cancel")
            
            dialog.add_response("background", "Run in Background")
            dialog.set_response_appearance("background", Adw.ResponseAppearance.SUGGESTED)
            
            if is_stopwatch_active and win.stopwatch.elapsed_seconds >= 300:
                dialog.add_response("save_quit", "Save & Quit")
                dialog.add_response("quit", "Discard & Quit")
                dialog.set_response_appearance("quit", Adw.ResponseAppearance.DESTRUCTIVE)
            else:
                dialog.add_response("quit", "Quit")
                dialog.set_response_appearance("quit", Adw.ResponseAppearance.DESTRUCTIVE)
                
            def on_response(dialog, response):
                if response == "background":
                    win.set_visible(False)
                    if hasattr(win, "compact_window") and win.compact_window:
                        win.compact_window.set_visible(False)
                elif response == "save_quit":
                    win._on_sw_save_clicked(None)
                    self._do_quit()
                elif response == "quit":
                    self._do_quit()
                    
            dialog.connect("response", on_response)
            dialog.present()
        else:
            self._do_quit()

    def _on_quit_action(self, action, param):
        win = self.props.active_window
        if win:
            if hasattr(win, "main_window"):
                self._attempt_quit(win.main_window)
            else:
                self._attempt_quit(win)
        else:
            self._do_quit()

    def _on_take_break(self, action, param):
        win = self.props.active_window
        if win and hasattr(win, "timer"):
            win.timer.start()

    def _on_skip_break(self, action, param):
        win = self.props.active_window
        if win and hasattr(win, "timer"):
            win.timer.next_state()
            win.timer.start()

    def _on_start_pomodoro(self, action, param):
        win = self.props.active_window
        if win and hasattr(win, "timer"):
            win.timer.start()

    def _on_skip_pomodoro(self, action, param):
        win = self.props.active_window
        if win and hasattr(win, "timer"):
            win.timer.next_state()
            win.timer.start()

    def _on_toggle_compact(self, action, param):
        win = self.props.active_window
        if win:
            if hasattr(win, "main_window"):
                win._on_restore_clicked(None)
            elif hasattr(win, "_on_compact_clicked"):
                win._on_compact_clicked(None)

    def _on_preferences_action(self, action, param):
        from plumb.preferences import PlumbPreferencesWindow

        win = self.props.active_window
        prefs_win = PlumbPreferencesWindow(timer=win.timer, transient_for=win)
        prefs_win.present()

    def do_activate(self):
        # Load CSS
        css_provider = Gtk.CssProvider()
        import os
        from gi.repository import Gdk

        css_path = os.path.join(os.path.dirname(__file__), "style.css")
        css_provider.load_from_path(css_path)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        icons_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")
        icon_theme.add_search_path(os.path.abspath(icons_path))

        win = self.props.active_window
        if not win:
            win = PlumbWindow(application=self)

            def _on_window_close(*args):
                self._attempt_quit(win)
                return True

            win.connect("close-request", _on_window_close)
            
        if hasattr(win, "main_window"):
            win = win.main_window
            
        win.set_visible(True)
        win.present()
