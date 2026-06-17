import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gdk, Gio, GObject, GLib
from tapas.timer import TimerLogic, StopwatchLogic

class TapasWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Tapas")
        self.set_default_size(400, 500)
        self.set_resizable(False)

        # Pomodoro Logic
        self.timer = TimerLogic()
        self.timer.on_tick_callback = self._on_timer_tick
        self.timer.on_state_change_callback = self._on_state_change
        self.timer.on_finish_callback = self._on_timer_finish

        # Stopwatch Logic
        self.stopwatch = StopwatchLogic()
        self.stopwatch.on_tick_callback = self._on_stopwatch_tick
        
        # Main layout using Adw.ToolbarView
        self.toolbar_view = Adw.ToolbarView()
        self.set_content(self.toolbar_view)

        # Header Bar
        self.header = Adw.HeaderBar()
        self.toolbar_view.add_top_bar(self.header)

        # ----------------------------------------------------
        # The Carousel (Provides 1:1 swiping physics)
        # ----------------------------------------------------
        self.carousel = Adw.Carousel()
        self.carousel.set_spacing(24)
        self.carousel.set_interactive(True) # Allows swipe to pan
        self.toolbar_view.set_content(self.carousel)

        # ----------------------------------------------------
        # Dummy ViewStack for the Bottom Bar
        # ----------------------------------------------------
        self.view_stack = Adw.ViewStack()
        
        # We just add empty dummy boxes to the stack. The real content goes in the carousel.
        self.view_stack.add_titled_with_icon(Gtk.Box(), "pomodoro", "Pomodoro", "alarm-symbolic")
        self.view_stack.add_titled_with_icon(Gtk.Box(), "timer", "Timer", "document-open-recent-symbolic")
        self.view_stack.add_titled_with_icon(Gtk.Box(), "stats", "Stats", "graph-symbolic")

        self.switcher_bar = Adw.ViewSwitcherBar(stack=self.view_stack)
        self.switcher_bar.set_reveal(True)
        self.toolbar_view.add_bottom_bar(self.switcher_bar)

        # Sync the Carousel and the ViewStack
        self.carousel.connect("page-changed", self._on_carousel_page_changed)
        self.view_stack.connect("notify::visible-child", self._on_view_stack_changed)

        # ----------------------------------------------------
        # Menu Button & Symmetries
        # ----------------------------------------------------
        self.menu_button = Gtk.MenuButton()
        self.menu_button.set_icon_name("open-menu-symbolic")
        
        menu = Gio.Menu()
        menu.append("Keyboard Shortcuts", "win.show-help-overlay")
        menu.append("Preferences", "app.preferences")
        menu.append("About Tapas", "app.about")
        
        self.menu_button.set_menu_model(menu)
        self.header.pack_end(self.menu_button)

        self.balance_button = Gtk.MenuButton()
        self.balance_button.set_icon_name("open-menu-symbolic")
        self.balance_button.set_opacity(0)
        self.balance_button.set_sensitive(False)
        self.header.pack_start(self.balance_button)

        # ----------------------------------------------------
        # Build Real Pages and add to Carousel
        # ----------------------------------------------------
        self.pomodoro_page = self._build_pomodoro_page()
        self.timer_page = self._build_timer_page()
        self.stats_page = Gtk.Label(label="Stats coming soon...")
        
        self.carousel.append(self.pomodoro_page)
        self.carousel.append(self.timer_page)
        self.carousel.append(self.stats_page)
        
        # Initialize UI state
        self._update_time_display()
        self._set_running_ui_state(False)
        self.add_css_class("focus-window")
        
        self._update_sw_time_display()
        self._set_sw_running_ui_state(False)


    # --- Sync Callbacks ---

    def _on_carousel_page_changed(self, carousel, index):
        pages = ["pomodoro", "timer", "stats"]
        # When swiping finishes, update the bottom bar to match
        if self.view_stack.get_visible_child_name() != pages[index]:
            self.view_stack.set_visible_child_name(pages[index])

    def _on_view_stack_changed(self, stack, param):
        pages = ["pomodoro", "timer", "stats"]
        name = stack.get_visible_child_name()
        if name in pages:
            index = pages.index(name)
            # When bottom bar is clicked, smoothly scroll the carousel to match
            target_widget = self.carousel.get_nth_page(index)
            self.carousel.scroll_to(target_widget, True)

    # --- UI Builders ---

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
        
        middle_container = Gtk.CenterBox()
        middle_container.set_size_request(-1, 140)
        middle_container.set_center_widget(progress_box)
        page_box.append(middle_container)

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

        return page_box

    def _build_timer_page(self):
        page_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=48)
        page_box.set_valign(Gtk.Align.CENTER)
        page_box.set_halign(Gtk.Align.CENTER)
        page_box.set_margin_start(32)
        page_box.set_margin_end(32)
        page_box.set_margin_top(32)
        page_box.set_margin_bottom(32)
        
        # 1. Project Dropdown
        self.sw_project_dropdown = Gtk.DropDown.new_from_strings(["DSA / Project", "Web Development", "Reading"])
        self.sw_project_dropdown.set_halign(Gtk.Align.CENTER)
        page_box.append(self.sw_project_dropdown)

        # 2. Huge Timer Label
        self.sw_time_label = Gtk.Label(label="00:00")
        self.sw_time_label.add_css_class("huge-timer")
        
        middle_container = Gtk.CenterBox()
        middle_container.set_size_request(-1, 140)
        middle_container.set_center_widget(self.sw_time_label)
        page_box.append(middle_container)

        # 3. Action Buttons
        self.sw_action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        self.sw_action_box.set_halign(Gtk.Align.CENTER)
        
        self.sw_restart_btn = Gtk.Button(label="Restart")
        self.sw_restart_btn.add_css_class("action-pill")
        self.sw_restart_btn.connect("clicked", self._on_sw_restart_clicked)
        
        self.sw_play_pause_btn = Gtk.Button()
        self.sw_play_pause_btn.set_icon_name("media-playback-start-symbolic")
        self.sw_play_pause_btn.add_css_class("play-circular")
        self.sw_play_pause_btn.connect("clicked", self._on_sw_play_pause_clicked)
        
        self.sw_save_btn = Gtk.Button(label="Save")
        self.sw_save_btn.add_css_class("action-pill")
        self.sw_save_btn.connect("clicked", self._on_sw_save_clicked)
        
        self.sw_action_box.append(self.sw_restart_btn)
        self.sw_action_box.append(self.sw_play_pause_btn)
        self.sw_action_box.append(self.sw_save_btn)
        
        page_box.append(self.sw_action_box)

        return page_box

    # --- Pomodoro UI State Helper ---
    
    def _set_running_ui_state(self, is_running):
        """Updates buttons and dropdown based on whether the timer is ticking."""
        self.switcher_bar.set_sensitive(not is_running)
        self.carousel.set_interactive(not is_running) # Lock swiping
        
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

    # --- Pomodoro Button Callbacks ---
    
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

    # --- Pomodoro Timer Callbacks ---

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

    # --- Stopwatch UI State Helper ---

    def _set_sw_running_ui_state(self, is_running):
        self.switcher_bar.set_sensitive(not is_running)
        self.carousel.set_interactive(not is_running) # Lock swiping
        
        if is_running:
            self.sw_play_pause_btn.set_icon_name("media-playback-pause-symbolic")
            self.sw_restart_btn.set_sensitive(False)
            self.sw_save_btn.set_sensitive(False)
            
            self.sw_project_dropdown.set_sensitive(False)
            self.sw_project_dropdown.set_show_arrow(False)
            self.sw_project_dropdown.remove_css_class("pill")
            self.sw_project_dropdown.add_css_class("flat")
            self.sw_project_dropdown.add_css_class("title-4")
        else:
            self.sw_play_pause_btn.set_icon_name("media-playback-start-symbolic")
            self.sw_restart_btn.set_sensitive(True)
            self.sw_save_btn.set_sensitive(True)
            
            self.sw_project_dropdown.set_sensitive(True)
            self.sw_project_dropdown.set_show_arrow(True)
            self.sw_project_dropdown.remove_css_class("flat")
            self.sw_project_dropdown.remove_css_class("title-4")
            self.sw_project_dropdown.add_css_class("pill")

    # --- Stopwatch Callbacks ---

    def _on_sw_play_pause_clicked(self, button):
        if self.stopwatch.is_running:
            self.stopwatch.pause()
            self._set_sw_running_ui_state(False)
        else:
            self.stopwatch.start()
            self._set_sw_running_ui_state(True)

    def _on_sw_restart_clicked(self, button):
        self.stopwatch.reset()
        self._set_sw_running_ui_state(False)
        self._update_sw_time_display()

    def _on_sw_save_clicked(self, button):
        # We will handle saving to DB later.
        # For now, just reset the stopwatch.
        self.stopwatch.reset()
        self._set_sw_running_ui_state(False)
        self._update_sw_time_display()

    def _update_sw_time_display(self):
        secs = self.stopwatch.elapsed_seconds
        m = secs // 60
        s = secs % 60
        self.sw_time_label.set_label(f"{m:02d}:{s:02d}")

    def _on_stopwatch_tick(self, elapsed_seconds):
        self._update_sw_time_display()
