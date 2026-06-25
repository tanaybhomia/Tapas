import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio
from tapas.window import TapasWindow

class TapasApplication(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id='com.github.tanay.Tapas',
            flags=Gio.ApplicationFlags.FLAGS_NONE
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
        
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", self._on_quit_action)
        self.add_action(quit_action)
        self.set_accels_for_action("app.quit", ["<Primary>q"])

    def _on_quit_action(self, action, param):
        import sys
        win = self.props.active_window
        if win and hasattr(win, 'timer') and win.timer and getattr(win.timer, 'dnd_sync', False):
            win.timer._set_gnome_dnd(False)
        self.quit()
        sys.exit(0)

    def _on_take_break(self, action, param):
        win = self.props.active_window
        if win and hasattr(win, 'timer'):
            win.timer.start()

    def _on_skip_break(self, action, param):
        win = self.props.active_window
        if win and hasattr(win, 'timer'):
            win.timer.next_state()
            win.timer.start()

    def _on_preferences_action(self, action, param):
        from tapas.preferences import TapasPreferencesWindow
        win = self.props.active_window
        prefs_win = TapasPreferencesWindow(timer=win.timer, transient_for=win)
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
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        
        icon_theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
        icons_path = os.path.join(os.path.dirname(__file__), "..", "assets", "icons")
        icon_theme.add_search_path(os.path.abspath(icons_path))

        win = self.props.active_window
        if not win:
            win = TapasWindow(application=self)
            def _on_window_close(*args):
                import sys
                if hasattr(win, 'timer') and win.timer and getattr(win.timer, 'dnd_sync', False):
                    win.timer._set_gnome_dnd(False)
                self.quit()
                sys.exit(0)
            win.connect("close-request", _on_window_close)
        win.present()
