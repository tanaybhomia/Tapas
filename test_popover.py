import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

def main():
    app = Gtk.Application()
    def on_activate(app):
        win = Gtk.ApplicationWindow(application=app)
        win.set_default_size(300, 300)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_halign(Gtk.Align.CENTER)
        box.set_valign(Gtk.Align.CENTER)
        
        dd = Gtk.DropDown.new_from_strings(["Short", "A very very long string indeed"])
        box.append(dd)
        
        popover = dd.get_last_child()
        if isinstance(popover, Gtk.Popover):
            popover.set_halign(Gtk.Align.CENTER)
            popover.set_position(Gtk.PositionType.BOTTOM)
            print("Popover aligned center!")
        
        win.set_child(box)
        win.present()
    app.connect('activate', on_activate)
    app.run(None)

if __name__ == '__main__': main()
