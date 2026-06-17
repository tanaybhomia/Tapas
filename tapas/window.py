import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gdk, Gio, GObject
from tapas.timer import TimerLogic

class TapasWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Tapas")
        self.set_default_size(400, 500)

        self.timer = TimerLogic()
        self.timer.on_tick_callback = self._on_timer_tick
        self.timer.on_state_change_callback = self._on_state_change
        self.timer.on_finish_callback = self._on_timer_finish
        
        # Main layout using Adw.ToolbarView
        self.toolbar_view = Adw.ToolbarView()
        self.set_content(self.toolbar_view)

        # Header Bar with View Switcher
        self.header = Adw.HeaderBar()
        self.toolbar_view.add_top_bar(self.header)

        # View Switcher (Pomodoro / Timer / Stats)
        self.view_stack = Adw.ViewStack()
        self.toolbar_view.set_content(self.view_stack)

        # Bottom Switcher Bar (Always Visible)
        self.switcher_bar = Adw.ViewSwitcherBar(stack=self.view_stack)
        self.switcher_bar.set_reveal(True)
        self.toolbar_view.add_bottom_bar(self.switcher_bar)

        # Main Menu (Hamburger) in the HeaderBar
        self.menu_button = Gtk.MenuButton()
        self.menu_button.set_icon_name("open-menu-symbolic")
        
        menu = Gio.Menu()
        menu.append("Keyboard Shortcuts", "win.show-help-overlay")
        menu.append("Preferences", "app.preferences")
        menu.append("About Tapas", "app.about")
        
        self.menu_button.set_menu_model(menu)
        self.header.pack_end(self.menu_button)

        # Invisible matching button on the left to guarantee perfect mathematical and visual symmetry
        self.balance_button = Gtk.MenuButton()
        self.balance_button.set_icon_name("open-menu-symbolic")
        self.balance_button.set_opacity(0)
        self.balance_button.set_sensitive(False)
        self.header.pack_start(self.balance_button)

        # Build the pages
        self._build_pomodoro_page()
        
        # Initialize UI state
        self._update_time_display()
        self._set_running_ui_state(False)
        self.add_css_class("focus-window")

    def _build_pomodoro_page(self):
        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=48)
        page_box.set_valign(Gtk.Align.CENTER)
        page_box.set_halign(Gtk.Align.CENTER)
        page_box.set_margin_start(32)
        page_box.set_margin_end(32)
        page_box.set_margin_top(32)
        page_box.set_margin_bottom(32)
        
        # 1. Project Dropdown
        self.project_dropdown = Gtk.DropDown.new_from_strings(["DSA / Project", "Web Development", "Reading"])
        self.project_dropdown.set_halign(Gtk.Align.CENTER)
        page_box.append(self.project_dropdown)

        # 2. Progress Bar and Time Labels
        progress_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_fraction(0.0)
        self.progress_bar.set_hexpand(True)
        self.progress_bar.add_css_class("focus-state") # Default state
        progress_box.append(self.progress_bar)
        
        # Time Labels
        time_labels_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        
        self.elapsed_label = Gtk.Label(label="00:00")
        self.elapsed_label.add_css_class("title-1")
        
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        
        self.total_label = Gtk.Label(label="25:00")
        self.total_label.add_css_class("title-1")
        
        time_labels_box.append(self.elapsed_label)
        time_labels_box.append(spacer)
        time_labels_box.append(self.total_label)
        
        progress_box.append(time_labels_box)
        page_box.append(progress_box)

        # 3. Action Buttons
        self.action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self.action_box.set_halign(Gtk.Align.CENTER)
        
        self.restart_btn = Gtk.Button(label="Restart")
        self.restart_btn.add_css_class("action-pill")
        self.restart_btn.connect("clicked", self._on_restart_clicked)
        
        self.play_pause_btn = Gtk.Button()
        self.play_pause_btn.set_icon_name("media-playback-start-symbolic")
        self.play_pause_btn.add_css_class("play-circular")
        self.play_pause_btn.connect("clicked", self._on_play_pause_clicked)
        
        self.break_btn = Gtk.Button(label="Skip")
        self.break_btn.add_css_class("action-pill")
        self.break_btn.connect("clicked", self._on_break_clicked)
        
        self.action_box.append(self.restart_btn)
        self.action_box.append(self.play_pause_btn)
        self.action_box.append(self.break_btn)
        
        page_box.append(self.action_box)

        self.view_stack.add_titled_with_icon(
            page_box, "pomodoro", "Pomodoro", "alarm-symbolic"
        )

        # Placeholders
        self.view_stack.add_titled_with_icon(
            Gtk.Label(label="Stopwatch Timer coming soon..."), "timer", "Timer", "document-open-recent-symbolic"
        )
        self.view_stack.add_titled_with_icon(
            Gtk.Label(label="Stats coming soon..."), "stats", "Stats", "utilities-system-monitor-symbolic"
        )

    # --- UI State Helper ---
    
    def _set_running_ui_state(self, is_running):
        """Updates buttons and dropdown based on whether the timer is ticking."""
        if is_running:
            self.play_pause_btn.set_icon_name("media-playback-pause-symbolic")
            self.restart_btn.set_sensitive(False)
            self.break_btn.set_sensitive(False)
            
            # Make the dropdown look like a static heading
            self.project_dropdown.set_sensitive(False)
            self.project_dropdown.set_show_arrow(False)
            self.project_dropdown.remove_css_class("pill")
            self.project_dropdown.add_css_class("flat")
            self.project_dropdown.add_css_class("title-4") # Make it slightly larger like a heading
        else:
            self.play_pause_btn.set_icon_name("media-playback-start-symbolic")
            self.restart_btn.set_sensitive(True)
            self.break_btn.set_sensitive(True)
            
            # Re-enable the dropdown
            self.project_dropdown.set_sensitive(True)
            self.project_dropdown.set_show_arrow(True)
            self.project_dropdown.remove_css_class("flat")
            self.project_dropdown.remove_css_class("title-4")
            self.project_dropdown.add_css_class("pill")


    # --- Button Callbacks ---
    
    def _on_play_pause_clicked(self, button):
        if self.timer.is_running:
            self.timer.pause()
            self._set_running_ui_state(False)
        else:
            self.timer.start()
            self._set_running_ui_state(True)

    def _on_restart_clicked(self, button):
        self.timer.reset()
        self._set_running_ui_state(False)
        self._update_time_display()

    def _on_break_clicked(self, button):
        self.timer.pause()
        self.timer.next_state()
        self._set_running_ui_state(False)
        self._update_time_display()

    # --- Timer Callbacks ---

    def _update_time_display(self):
        time_left = self.timer.time_left
        total_time = self.timer.durations[self.timer.state] * 60
        elapsed_time = total_time - time_left
        
        el_min = elapsed_time // 60
        el_sec = elapsed_time % 60
        self.elapsed_label.set_label(f"{el_min:02d}:{el_sec:02d}")
        
        tot_min = total_time // 60
        tot_sec = total_time % 60
        self.total_label.set_label(f"{tot_min:02d}:{tot_sec:02d}")
        
        if total_time > 0:
            self.progress_bar.set_fraction(elapsed_time / total_time)
        else:
            self.progress_bar.set_fraction(0.0)

    def _on_timer_tick(self, time_left):
        self._update_time_display()

    def _on_state_change(self, new_state):
        # Update progress bar colors
        self.progress_bar.remove_css_class("focus-state")
        self.progress_bar.remove_css_class("short-break-state")
        self.progress_bar.remove_css_class("long-break-state")
        
        # Update window background tint
        self.remove_css_class("focus-window")
        self.remove_css_class("short-break-window")
        self.remove_css_class("long-break-window")
        
        if new_state == "Focus":
            self.progress_bar.add_css_class("focus-state")
            self.add_css_class("focus-window")
        elif new_state == "Short Break":
            self.progress_bar.add_css_class("short-break-state")
            self.add_css_class("short-break-window")
        elif new_state == "Long Break":
            self.progress_bar.add_css_class("long-break-state")
            self.add_css_class("long-break-window")

        self._update_time_display()
        self._set_running_ui_state(False)

    def _on_timer_finish(self):
        self._set_running_ui_state(False)
        self._update_time_display()
