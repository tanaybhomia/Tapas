#!/usr/bin/env python3
import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from tapas.application import TapasApplication

def main():
    app = TapasApplication()
    return app.run(sys.argv)

if __name__ == '__main__':
    sys.exit(main())
