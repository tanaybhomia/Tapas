import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk

def main():
    app = Gtk.Application()
    def on_activate(app):
        win = Gtk.ApplicationWindow(application=app)
        model = Gtk.StringList()
        model.append("Test 1")
        model.append("Test 2")
        
        dd = Gtk.DropDown.new(model=model)
        
        factory = Gtk.SignalListItemFactory()
        def on_setup(f, item):
            label = Gtk.Label()
            label.set_halign(Gtk.Align.CENTER)
            item.set_child(label)
        def on_bind(f, item):
            label = item.get_child()
            string_obj = item.get_item()
            label.set_text(string_obj.get_string())
            
        factory.connect("setup", on_setup)
        factory.connect("bind", on_bind)
        
        dd.set_factory(factory)
        dd.set_list_factory(factory)
        
        win.set_child(dd)
        win.present()
    app.connect('activate', on_activate)
    app.run(None)

if __name__ == '__main__': main()
