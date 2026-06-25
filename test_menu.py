import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw

def main():
    app = Adw.Application()
    def on_activate(app):
        win = Adw.ApplicationWindow(application=app)
        header = Adw.HeaderBar()
        mb = Gtk.MenuButton()
        mb.set_icon_name("open-menu-symbolic")
        
        popover = Gtk.Popover()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        vbox.set_margin_top(12)
        vbox.set_margin_bottom(12)
        vbox.set_margin_start(12)
        vbox.set_margin_end(12)
        
        theme_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        theme_box.set_halign(Gtk.Align.CENTER)
        
        btn1 = Gtk.Button(label="S")
        btn1.add_css_class("circular")
        btn1.set_size_request(48, 48)
        btn2 = Gtk.Button(label="L")
        btn2.add_css_class("circular")
        btn2.set_size_request(48, 48)
        btn3 = Gtk.Button(label="D")
        btn3.add_css_class("circular")
        btn3.set_size_request(48, 48)
        
        theme_box.append(btn1)
        theme_box.append(btn2)
        theme_box.append(btn3)
        
        vbox.append(theme_box)
        
        btn_pref = Gtk.Button(label="Preferences")
        btn_pref.add_css_class("flat")
        vbox.append(btn_pref)
        
        popover.set_child(vbox)
        mb.set_popover(popover)
        
        header.pack_end(mb)
        
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.append(header)
        win.set_content(box)
        win.set_default_size(400, 300)
        win.present()
        
    app.connect('activate', on_activate)
    app.run(None)

if __name__ == '__main__': main()
