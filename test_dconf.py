import gi
gi.require_version('Gio', '2.0')
from gi.repository import Gio
import sys

settings = Gio.Settings.new("org.gnome.desktop.notifications")
settings.set_boolean("show-banners", False)
sys.exit(0)
