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
        win = self.props.active_window
        if not win:
            win = TapasWindow(application=self)
        win.present()
