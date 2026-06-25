import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib

def main():
    app = Gtk.Application()
    def on_activate(app):
        win = Gtk.ApplicationWindow(application=app)
        mb = Gtk.MenuButton()
        
        menu = Gio.Menu()
        item = Gio.MenuItem.new(None, None)
        item.set_attribute_value("custom", GLib.Variant("s", "theme-selector"))
        menu.append_item(item)
        menu.append("Test", "app.test")
        
        popover = Gtk.PopoverMenu.new_from_model(menu)
        
        box = Gtk.Box()
        btn = Gtk.Button(label="Custom Widget!")
        box.append(btn)
        
        popover.add_child(box, "theme-selector")
        mb.set_popover(popover)
        
        win.set_child(mb)
        win.present()
    app.connect('activate', on_activate)
    app.run(None)

if __name__ == '__main__': main()
