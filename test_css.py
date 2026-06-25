import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk

css = b"""
checkbutton.theme-selector > check {
    min-width: 48px;
    min-height: 48px;
    border-radius: 24px;
    color: transparent; /* hides checkmark */
    background-color: transparent;
    border: 1px solid alpha(currentColor, 0.2);
}
checkbutton.theme-selector.system-theme > check {
    background-image: linear-gradient(-45deg, #242424 50%, #ffffff 50%);
}
checkbutton.theme-selector.light-theme > check {
    background-color: #ffffff;
    background-image: none;
}
checkbutton.theme-selector.dark-theme > check {
    background-color: #242424;
    background-image: none;
}
checkbutton.theme-selector:checked > check {
    box-shadow: 0 0 0 2px @accent_bg_color;
}
"""

def main():
    app = Gtk.Application()
    def on_activate(app):
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
        
        win = Gtk.ApplicationWindow(application=app)
        box = Gtk.Box(spacing=16, margin_top=20, margin_start=20)
        
        c1 = Gtk.CheckButton()
        c1.add_css_class("theme-selector")
        c1.add_css_class("system-theme")
        
        c2 = Gtk.CheckButton(group=c1)
        c2.add_css_class("theme-selector")
        c2.add_css_class("light-theme")
        
        c3 = Gtk.CheckButton(group=c1)
        c3.add_css_class("theme-selector")
        c3.add_css_class("dark-theme")
        
        box.append(c1)
        box.append(c2)
        box.append(c3)
        
        win.set_child(box)
        win.present()
    app.connect('activate', on_activate)
    app.run(None)

if __name__ == '__main__': main()
