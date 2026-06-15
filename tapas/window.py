import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gdk
from tapas.timer import TimerLogic

class TapasWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Tapas")
        self.set_default_size(500, 600)

        self.timer = TimerLogic()
        self.timer.on_tick_callback = self._on_timer_tick
        
        # Main layout using Adw.ToolbarView
        self.toolbar_view = Adw.ToolbarView()
        self.set_content(self.toolbar_view)

        # Header Bar with View Switcher
        self.header = Adw.HeaderBar()
        self.toolbar_view.add_top_bar(self.header)

        # View Switcher (Pomodoro / Timer / Stats)
        self.view_stack = Adw.ViewStack()
        self.toolbar_view.set_content(self.view_stack)

        self.view_switcher_title = Adw.ViewSwitcherTitle(stack=self.view_stack)
        self.header.set_title_widget(self.view_switcher_title)

        # Build the pages
        self._build_pomodoro_page()
        
        # Setup keyboard shortcuts (Spacebar to play/pause)
        self._setup_key_controller()

    def _build_pomodoro_page(self):
        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        page_box.set_valign(Gtk.Align.CENTER)
        page_box.set_halign(Gtk.Align.CENTER)

        # The big clock display
        self.time_label = Gtk.Label(label="25:00")
        self.time_label.add_css_class("title-1")
        # We can make it massive using custom CSS later, for now we use title-1
        self.time_label.set_margin_bottom(24)

        # The action buttons (hidden by default)
        self.action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.action_box.set_halign(Gtk.Align.CENTER)
        self.action_box.set_visible(False)

        save_btn = Gtk.Button(label="Save Session")
        save_btn.add_css_class("suggested-action")
        save_btn.add_css_class("pill")
        
        save_exit_btn = Gtk.Button(label="Save and Exit")
        save_exit_btn.add_css_class("destructive-action")
        save_exit_btn.add_css_class("pill")

        self.action_box.append(save_btn)
        self.action_box.append(save_exit_btn)

        # Instruction label
        self.instruction_label = Gtk.Label(label="Press Space to Start")
        self.instruction_label.add_css_class("dim-label")

        page_box.append(self.time_label)
        page_box.append(self.action_box)
        page_box.append(self.instruction_label)

        self.view_stack.add_titled_with_icon(
            page_box, "pomodoro", "Pomodoro", "alarm-symbolic"
        )

        # Placeholders for the other tabs
        self.view_stack.add_titled_with_icon(
            Gtk.Label(label="Stopwatch Timer coming soon..."), "timer", "Timer", "document-open-recent-symbolic"
        )
        self.view_stack.add_titled_with_icon(
            Gtk.Label(label="Stats coming soon..."), "stats", "Stats", "utilities-system-monitor-symbolic"
        )

    def _setup_key_controller(self):
        key_ctrl = Gtk.EventControllerKey()
        key_ctrl.connect("key-pressed", self._on_key_pressed)
        self.add_controller(key_ctrl)

    def _on_key_pressed(self, controller, keyval, keycode, state):
        if keyval == Gdk.KEY_space:
            if self.timer.is_running:
                # Pause and show options
                self.timer.pause()
                self.action_box.set_visible(True)
                self.instruction_label.set_label("Press Space to Resume")
            else:
                # Start/Resume and hide options
                self.timer.start()
                self.action_box.set_visible(False)
                self.instruction_label.set_label("Focusing... (Press Space to Pause)")
            return True # Event handled
        return False

    def _on_timer_tick(self, time_left):
        minutes = time_left // 60
        seconds = time_left % 60
        self.time_label.set_label(f"{minutes:02d}:{seconds:02d}")

