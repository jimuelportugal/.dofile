#!/usr/bin/env python3
import math
import gi
import os
import sys
import glob
import signal

LOCK_FILE = "/tmp/hypr_app_drawer.pid"

# Single-instance toggle: if already running, signal it to slide down
if os.path.exists(LOCK_FILE):
    try:
        with open(LOCK_FILE, "r") as f:
            pid = int(f.read().strip())
        os.kill(pid, signal.SIGUSR1)
        sys.exit(0)
    except (ProcessLookupError, ValueError):
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)

with open(LOCK_FILE, "w") as f:
    f.write(str(os.getpid()))

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, Gio, GtkLayerShell, GLib

CATEGORIES = {
    "SYSTEM": [
        "blueman-manager.desktop",
        "btop.desktop",
        "org.fedoraproject.MediaWriter.desktop",
        "org.gnome.baobab.desktop",
        "org.gnome.Characters.desktop",
        "org.gnome.clocks.desktop",
        "org.gnome.Connections.desktop",
        "org.gnome.DiskUtility.desktop",
        "org.gnome.Logs.desktop",
        "org.gnome.SystemMonitor.desktop",
    ],
    "MY APPS": [
        "brave-origin.desktop",
        "org.mozilla.firefox.desktop",
        "net.blockbench.blockbench.desktop",
        "org.gnome.Software.desktop",
        "thunar.desktop",
    ],
    "CODING": [
        "code.desktop",
        "Godot Engine.desktop",
        "org.gnome.Boxes.desktop",
        "org.gnome.Ptyxis.desktop",
        "org.gnome.TextEditor.desktop",
        "scrcpy-console.desktop",
        "scrcpy.desktop",
        "org.gnome.Contacts.desktop",
    ],
    "GAMES": [
        "steam.desktop",
        "Don't Starve Together.desktop",
        "Kenshi.desktop",
        "org.ppsspp.PPSSPP.desktop",
        "Project Zomboid.desktop",
        "R.E.P.O..desktop",
        "RIMWORLD.desktop",
        "Terraria.desktop",
        "The Elder Scrolls V Skyrim Special Edition.desktop",
        "Valheim.desktop",
    ],
    "DOCUMENT ETC": [
        "libreoffice-calc.desktop",
        "libreoffice-writer.desktop",
        "libreoffice-impress.desktop",
        "org.gnome.Loupe.desktop",
        "org.gnome.Nautilus.desktop",
        "org.gnome.Papers.desktop",
        "org.gnome.Showtime.desktop",
        "org.gnome.Decibels.desktop",
        "org.gnome.Snapshot.desktop",
        "org.gnome.SimpleScan.desktop",
        "org.kde.krita.desktop",
    ],
    "CONFIGS": [
        "fcitx5-configtool.desktop",
        "io.github.jeffshee.Hidamari.desktop",
        "kbd-layout-viewer5.desktop",
        "nwg-panel-config.desktop",
        "org.gnome.ColorProfileViewer.desktop",
        "org.gnome.font-viewer.desktop",
        "rofi.desktop",
        "rofi-theme-selector.desktop",
        "rygel-preferences.desktop",
        "thunar-bulk-rename.desktop",
        "thunar-settings.desktop",
    ]
}

def get_installed_apps():
    apps = {}
    search_paths = [
        os.path.expanduser("~/.local/share/applications"),
        "/var/lib/flatpak/exports/share/applications",
        os.path.expanduser("~/.local/share/flatpak/exports/share/applications"),
        "/usr/local/share/applications",
        "/usr/share/applications"
    ]
    
    for base_dir in search_paths:
        if not os.path.isdir(base_dir):
            continue
        for filepath in glob.glob(os.path.join(base_dir, "*.desktop")):
            filename = os.path.basename(filepath)
            if filename in apps:
                continue
            
            try:
                app_info = Gio.DesktopAppInfo.new_from_filename(filepath)
            except Exception:
                app_info = None

            if not app_info:
                continue

            icon = app_info.get_icon()
            icon_name = icon.to_string() if icon else "application-x-executable"

            app_data = {
                "name": app_info.get_name() or filename.replace(".desktop", ""),
                "icon": icon_name,
                "app_info": app_info,
            }
            apps[filename] = app_data
            apps[filename.lower()] = app_data
            apps[filename.replace(".desktop", "")] = app_data
            apps[filename.replace(".desktop", "").lower()] = app_data

    return apps

class AppDrawer(Gtk.Window):
    def __init__(self):
        super().__init__()
        
        all_apps = get_installed_apps()
        categorized_apps = {cat: [] for cat in CATEGORIES}

        for cat, app_filenames in CATEGORIES.items():
            for filename in app_filenames:
                clean_name = filename.strip()
                if clean_name in all_apps:
                    categorized_apps[cat].append(all_apps[clean_name])
                elif clean_name.lower() in all_apps:
                    categorized_apps[cat].append(all_apps[clean_name.lower()])

        # Layer-shell configuration
        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)
        
        # Anchor to bottom edge
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, False)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.LEFT, False)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, False)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.set_app_paintable(True)

        self.flare_size = 36
        self.corner_radius = 16
        self.drawer_height = 620
        self.drawer_width = 880 + (self.flare_size * 2)
        self.set_size_request(self.drawer_width, self.drawer_height)

        # Animation state
        self.current_offset = self.drawer_height
        self.anim_id = None
        self.is_closing = False

        # Set initial hidden margin
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, -self.current_offset)

        self.connect("draw", self.on_draw)
        self.connect("key-press-event", self.on_key_press)
        self.connect("focus-out-event", self.on_focus_out)

        outer_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        outer_box.set_margin_top(28)
        outer_box.set_margin_bottom(16)
        outer_box.set_margin_start(self.flare_size + 24)
        outer_box.set_margin_end(self.flare_size + 24)
        self.add(outer_box)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.EXTERNAL)
        outer_box.pack_start(scrolled, True, True, 0)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_margin_top(12)
        scrolled.add(main_box)

        for i, (cat, cat_apps) in enumerate(categorized_apps.items()):
            if not cat_apps:
                continue

            if i > 0:
                divider = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                divider.set_margin_top(12)
                divider.set_margin_bottom(12)
                main_box.pack_start(divider, False, False, 0)

            grid = Gtk.FlowBox()
            grid.set_valign(Gtk.Align.START)
            grid.set_max_children_per_line(5)
            grid.set_min_children_per_line(4)
            grid.set_selection_mode(Gtk.SelectionMode.NONE)
            grid.set_homogeneous(True)
            grid.set_row_spacing(16)
            grid.set_column_spacing(16)

            for app_data in cat_apps:
                btn = self.create_app_button(app_data)
                grid.add(btn)

            main_box.pack_start(grid, False, False, 0)

        # Trigger smooth entry slide
        self.start_animation(target_offset=0, on_done=None)

    def start_animation(self, target_offset, on_done=None):
        if self.anim_id is not None:
            GLib.source_remove(self.anim_id)
            self.anim_id = None

        def step():
            diff = target_offset - self.current_offset
            if abs(diff) <= 4:
                self.current_offset = target_offset
                GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, -self.current_offset)
                self.anim_id = None
                if on_done:
                    on_done()
                return False

            step_size = max(5, int(abs(diff) * 0.32))
            if diff < 0:
                self.current_offset -= step_size
            else:
                self.current_offset += step_size

            GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, -self.current_offset)
            return True

        self.anim_id = GLib.timeout_add(10, step)

    def slide_close(self):
        if self.is_closing:
            return
        self.is_closing = True
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.NONE)
        self.start_animation(target_offset=self.drawer_height, on_done=self.cleanup_and_quit)

    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        r = self.corner_radius
        f = self.flare_size

        cr.set_operator(0)
        cr.paint()
        cr.set_operator(2)

        # Silhouette path
        cr.move_to(0, height)
        cr.arc_negative(0, height - f, f, math.pi / 2, 0)
        cr.line_to(f, r)
        cr.arc(f + r, r, r, math.pi, 3 * math.pi / 2)
        cr.line_to(width - f - r, 0)
        cr.arc(width - f - r, r, r, 3 * math.pi / 2, 0)
        cr.line_to(width - f, height - f)
        cr.arc_negative(width, height - f, f, math.pi, math.pi / 2)
        cr.line_to(0, height)
        cr.close_path()

        # Solid dark gray
        cr.set_source_rgba(0.09, 0.09, 0.10, 1.0)
        cr.fill_preserve()

        # Subtle border
        cr.set_source_rgba(0.9, 0.9, 0.9, 0.12)
        cr.set_line_width(1.0)
        cr.stroke()

        return False

    def create_app_button(self, app_data):
        btn = Gtk.Button()
        btn.get_style_context().add_class("app-button")
        btn.set_relief(Gtk.ReliefStyle.NONE)
        btn.set_can_focus(False)
        btn.connect("clicked", lambda w: self.launch_app(app_data["app_info"]))

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        box.set_halign(Gtk.Align.CENTER)

        image = Gtk.Image.new_from_icon_name(app_data["icon"], Gtk.IconSize.DIALOG)
        image.set_pixel_size(48)

        lbl = Gtk.Label(label=app_data["name"])
        lbl.set_max_width_chars(12)
        lbl.set_ellipsize(3)
        lbl.set_line_wrap(True)

        box.pack_start(image, False, False, 0)
        box.pack_start(lbl, False, False, 0)
        btn.add(box)
        return btn

    def launch_app(self, app_info):
        app_info.launch([], None)
        self.slide_close()

    def cleanup_and_quit(self):
        if os.path.exists(LOCK_FILE):
            try:
                os.remove(LOCK_FILE)
            except OSError:
                pass
        Gtk.main_quit()

    def on_focus_out(self, widget, event):
        self.slide_close()
        return False

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.slide_close()
            return True
        return False

css_provider = Gtk.CssProvider()
css = b"""
window {
    background-color: transparent;
    font-family: "JetBrainsMono Nerd Font", "JetBrains Mono", sans-serif;
}
flowboxchild,
flowboxchild:hover,
flowboxchild:selected,
flowboxchild:focus {
    background: transparent;
    outline: none;
    border: none;
    box-shadow: none;
    -gtk-outline-radius: 0;
}
button.app-button {
    background: transparent;
    border: none;
    outline: none;
    box-shadow: none;
    margin: 0;
    padding-top: 10px;
    padding-bottom: 6px;
    padding-left: 8px;
    padding-right: 8px;
    color: rgba(255, 255, 255, 0.75);
    font-size: 12px;
    transition: padding-top 160ms cubic-bezier(0.2, 0, 0, 1),
                padding-bottom 160ms cubic-bezier(0.2, 0, 0, 1),
                color 160ms ease;
}
button.app-button:hover {
    background: transparent;
    border: none;
    outline: none;
    box-shadow: none;
    margin: 0;
    padding-top: 4px;
    padding-bottom: 12px;
    color: #ffffff;
}
separator {
    background-color: rgba(255, 255, 255, 0.10);
}
scrollbar,
scrollbar button,
scrollbar slider {
    opacity: 0;
    min-width: 0px;
    min-height: 0px;
    background: transparent;
    border: none;
}
"""
css_provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(),
    css_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

if __name__ == "__main__":
    win = AppDrawer()
    win.connect("destroy", lambda w: win.cleanup_and_quit())
    
    # Catch toggle signal and cleanly slide down
    signal.signal(signal.SIGUSR1, lambda s, f: GLib.idle_add(win.slide_close))
    signal.signal(signal.SIGTERM, lambda s, f: GLib.idle_add(win.slide_close))
    
    win.show_all()
    Gtk.main()
# // citation: none