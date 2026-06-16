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

        win = self.props.active_window
        if not win:
            win = TapasWindow(application=self)
        win.present()
