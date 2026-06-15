import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw

class TapasWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Tapas")
        self.set_default_size(800, 600)

        # Main layout
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_content(self.main_box)

        # Header Bar
        self.header = Adw.HeaderBar()
        self.main_box.append(self.header)

        # Add a welcome label for now
        self.welcome_label = Gtk.Label(label="Welcome to Tapas! Your Focus App.", 
                                       vexpand=True, 
                                       hexpand=True)
        self.main_box.append(self.welcome_label)
