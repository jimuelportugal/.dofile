import json
import math
import os
import signal
import sys

LOCK_FILE = "/tmp/hypr_app_drawer.pid"

def check_single_instance():
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

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, Gio, GtkLayerShell, GLib

CATEGORY_ORDER = ["SYSTEM", "MY APPS", "CODING", "GAMES", "DOCUMENT ETC", "CONFIGS"]

def load_pinned_overrides():
    """Load optional custom category mappings from drawer_pinned.json."""
    candidates = [
        os.path.expanduser("~/.config/hypr/drawer_pinned.json"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "drawer_pinned.json")
    ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("pinned_overrides", data)
            except Exception as e:
                print(f"[drawer.py] Warning: could not parse {path}: {e}", file=sys.stderr)
    return {}

def detect_category(filename, app_name, categories_str, pinned_overrides):
    """Categorize an application dynamically using XDG categories or user overrides."""
    fn_lower = filename.lower()
    fn_clean = fn_lower[:-8] if fn_lower.endswith(".desktop") else fn_lower
    name_lower = app_name.lower().strip()

    for p_name, p_cat in pinned_overrides.items():
        p_lower = p_name.lower()
        p_clean = p_lower[:-8] if p_lower.endswith(".desktop") else p_lower
        if fn_lower == p_lower or fn_clean == p_clean or name_lower == p_clean:
            return p_cat

    cats = set(c.strip().lower() for c in (categories_str or "").split(";") if c.strip())

    game_keywords = {
        "game", "emulator", "actiongame", "adventuregame", "arcadegame",
        "boardgame", "cardgame", "kidsgame", "logicgame", "roleplaying",
        "shooter", "simulation", "sportsgame", "strategygame"
    }
    if cats.intersection(game_keywords) or "steam" in fn_lower or "steam_app_" in fn_lower:
        return "GAMES"

    dev_keywords = {
        "development", "ide", "debugger", "revisioncontrol",
        "webdevelopment", "guidance", "terminal", "texteditor", "programming"
    }
    if cats.intersection(dev_keywords) or any(k in name_lower for k in ["code", "terminal", "ptyxis", "godot", "scrcpy"]):
        return "CODING"

    settings_keywords = {
        "settings", "desktopsettings", "hardwaresettings", "preferences", "security"
    }
    if cats.intersection(settings_keywords) or any(k in name_lower for k in ["setting", "config", "preference"]):
        return "CONFIGS"

    doc_keywords = {
        "office", "graphics", "audiovideo", "audio", "video", "music",
        "player", "recorder", "viewer", "rastergraphics", "2dgraphics",
        "vectorgraphics", "scanning", "photography", "publishing",
        "spreadsheet", "wordprocessor", "presentation"
    }
    if cats.intersection(doc_keywords):
        return "DOCUMENT ETC"

    sys_keywords = {
        "system", "monitor", "packagemanager", "core", "filesystem", "filetools"
    }
    if cats.intersection(sys_keywords) or any(k in name_lower for k in ["monitor", "disk", "writer"]):
        return "SYSTEM"

    return "MY APPS"

def get_installed_and_categorized_apps():
    """Discover all installed desktop apps via GLib and categorize them dynamically."""
    pinned_overrides = load_pinned_overrides()
    categorized_apps = {cat: [] for cat in CATEGORY_ORDER}

    seen_ids = set()
    seen_names = set()

    for app_info in Gio.AppInfo.get_all():
        if not app_info:
            continue

        if hasattr(app_info, "get_nodisplay") and app_info.get_nodisplay():
            continue

        app_id = app_info.get_id() or ""
        if app_id in seen_ids:
            continue
        seen_ids.add(app_id)

        app_name = app_info.get_name() or app_id.replace(".desktop", "")
        name_key = app_name.lower().strip()
        if name_key in seen_names:
            continue
        seen_names.add(name_key)

        icon = app_info.get_icon()
        icon_name = icon.to_string() if icon else "application-x-executable"
        categories_str = app_info.get_categories() if hasattr(app_info, "get_categories") else ""

        filename = app_id or (os.path.basename(app_info.get_filename()) if hasattr(app_info, "get_filename") and app_info.get_filename() else "")

        app_data = {
            "name": app_name,
            "icon": icon_name,
            "gicon": icon,
            "app_info": app_info,
            "filename": filename,
            "id": app_id,
        }

        cat = detect_category(filename, app_name, categories_str, pinned_overrides)
        if cat not in categorized_apps:
            categorized_apps[cat] = []
        categorized_apps[cat].append(app_data)

    pinned_keys = [k.lower().replace(".desktop", "") for k in pinned_overrides.keys()]
    for cat in categorized_apps:
        def sort_key(app):
            fn_key = app["filename"].lower().replace(".desktop", "")
            app_name_key = app["name"].lower().strip()
            for idx, p_key in enumerate(pinned_keys):
                if p_key in (fn_key, app_name_key) and pinned_overrides.get(list(pinned_overrides.keys())[idx]) == cat:
                    return (0, idx)
            return (1, app_name_key)

        categorized_apps[cat].sort(key=sort_key)

    return categorized_apps

class AppDrawer(Gtk.Window):
    def __init__(self):
        super().__init__()

        categorized_apps = get_installed_and_categorized_apps()

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)
        
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

        self.current_offset = self.drawer_height
        self.anim_id = None
        self.is_closing = False
        self.rule_active = False
        self.mouse_inside = False

        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, -self.current_offset)

        self.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK)
        self.connect("enter-notify-event", self.on_mouse_enter)
        self.connect("leave-notify-event", self.on_mouse_leave)
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
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
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

    def on_mouse_enter(self, widget, event):
        self.mouse_inside = True
        self.rule_active = True
        return False

    def on_mouse_leave(self, widget, event):
        self.mouse_inside = False
        return False

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

        cr.set_source_rgba(0.09, 0.09, 0.10, 1.0)
        cr.fill_preserve()

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

        gicon = app_data.get("gicon")
        icon_val = app_data.get("icon")
        if gicon:
            image = Gtk.Image.new_from_gicon(gicon, Gtk.IconSize.DIALOG)
        elif icon_val and os.path.isabs(icon_val) and os.path.exists(icon_val):
            image = Gtk.Image.new_from_file(icon_val)
        elif icon_val:
            image = Gtk.Image.new_from_icon_name(icon_val, Gtk.IconSize.DIALOG)
        else:
            image = Gtk.Image.new_from_icon_name("application-x-executable", Gtk.IconSize.DIALOG)
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
        if not self.rule_active or self.mouse_inside:
            return False
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
    font-family: "JetBrainsMono Nerd Font", "JetBrainsMono NF", "JetBrains Mono", "Font Awesome 6 Free", sans-serif;
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
if __name__ == "__main__":
    check_single_instance()

    screen = Gdk.Screen.get_default()
    if screen:
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    win = AppDrawer()
    win.connect("destroy", lambda w: win.cleanup_and_quit())
    
    signal.signal(signal.SIGUSR1, lambda s, f: GLib.idle_add(win.slide_close))
    signal.signal(signal.SIGTERM, lambda s, f: GLib.idle_add(win.slide_close))
    
    win.show_all()
    Gtk.main()
