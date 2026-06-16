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
