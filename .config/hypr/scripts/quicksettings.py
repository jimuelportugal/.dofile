#!/usr/bin/env python3
import os
import sys
import signal
import subprocess
import gi

LOCK_FILE = "/tmp/hypr_quicksettings.pid"

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
from gi.repository import Gtk, Gdk, GLib, GtkLayerShell

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, text=True).strip()
    except Exception:
        return ""

def get_wifi_state():
    out = run_cmd("nmcli radio wifi")
    return out.lower() == "enabled"

def get_bt_state():
    out = run_cmd("bluetoothctl show | grep 'Powered:'")
    return "yes" in out.lower()

def get_vol():
    out = run_cmd("pamixer --get-volume")
    return int(out) if out.isdigit() else 50

def get_audio_mute():
    out = run_cmd("pamixer --get-mute")
    return out.lower() == "true"

def get_mic_vol():
    out = run_cmd("pamixer --default-source --get-volume")
    return int(out) if out.isdigit() else 50

def get_mic_mute():
    out = run_cmd("pamixer --default-source --get-mute")
    return out.lower() == "true"

def get_brightness():
    out = run_cmd("brightnessctl -m | cut -d',' -f4 | tr -d '%'")
    return int(out) if out.isdigit() else 50

class QuickSettings(Gtk.Window):
    def __init__(self):
        super().__init__()

        GtkLayerShell.init_for_window(self)
        GtkLayerShell.set_namespace(self, "quicksettings")
        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)
        GtkLayerShell.set_keyboard_mode(self, GtkLayerShell.KeyboardMode.ON_DEMAND)

        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.TOP, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.TOP, 10)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 14)

        self.set_size_request(340, -1)
        self.connect("key-press-event", self.on_key_press)
        self.connect("focus-out-event", self.on_focus_out)

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.main_box.get_style_context().add_class("quicksettings-window")
        self.add(self.main_box)

        # ---------------- 1. WI-FI & BT TILES (SIDE BY SIDE) ----------------
        top_grid = Gtk.Grid()
        top_grid.set_column_spacing(10)
        top_grid.set_column_homogeneous(True)
        self.main_box.pack_start(top_grid, False, False, 0)

        self.wifi_btn = self.create_toggle_tile("Wi-Fi", "network-wireless-symbolic", get_wifi_state(), self.toggle_wifi)
        top_grid.attach(self.wifi_btn, 0, 0, 1, 1)

        self.bt_btn = self.create_toggle_tile("Bluetooth", "bluetooth-active-symbolic", get_bt_state(), self.toggle_bt)
        top_grid.attach(self.bt_btn, 1, 0, 1, 1)

        # ---------------- 2. CIRCULAR ACTION BUTTONS ----------------
        circle_grid = Gtk.Grid()
        circle_grid.set_column_spacing(12)
        circle_grid.set_row_spacing(12)
        circle_grid.set_column_homogeneous(True)
        self.main_box.pack_start(circle_grid, False, False, 0)

        self.audio_active = not get_audio_mute()
        self.audio_btn = self.create_circle_tile("Audio", "audio-volume-high-symbolic", self.audio_active, self.toggle_audio_mute)
        circle_grid.attach(self.audio_btn, 0, 0, 1, 1)

        self.mic_active = not get_mic_mute()
        self.mic_btn = self.create_circle_tile("Mic", "audio-input-microphone-symbolic", self.mic_active, self.toggle_mic_view)
        circle_grid.attach(self.mic_btn, 1, 0, 1, 1)

        self.shot_btn = self.create_circle_tile("Screenshot", "camera-photo-symbolic", False, self.action_screenshot)
        circle_grid.attach(self.shot_btn, 2, 0, 1, 1)

        self.settings_btn = self.create_circle_tile("Settings", "emblem-system-symbolic", False, self.action_settings)
        circle_grid.attach(self.settings_btn, 3, 0, 1, 1)

        self.main_box.pack_start(Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL), False, False, 0)

        # ---------------- 3. SLIDERS CONTAINER (4px GAP) ----------------
        self.slider_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.main_box.pack_start(self.slider_box, False, False, 0)

        # Brightness Slider
        self.bright_box = self.create_slider_row("display-brightness-symbolic", get_brightness(), self.on_bright_change)
        self.slider_box.pack_start(self.bright_box, False, False, 0)

        # Volume Slider
        self.vol_row = self.create_slider_row("audio-volume-high-symbolic", get_vol(), self.on_vol_change)
        self.slider_box.pack_start(self.vol_row, False, False, 0)

        # ---------------- 4. PRE-ALLOCATED MIC SLOT ----------------
        self.mic_stack = Gtk.Stack()
        self.mic_stack.set_homogeneous(True)
        self.mic_stack.set_transition_type(Gtk.StackTransitionType.NONE)

        # Real Mic Slider Row
        self.mic_row = self.create_slider_row("audio-input-microphone-symbolic", get_mic_vol(), self.on_mic_change)
        self.mic_stack.add_named(self.mic_row, "slider")

        # Invisible Placeholder matching exact row height
        self.placeholder = Gtk.Box()
        self.placeholder.set_size_request(-1, 18)
        self.placeholder.set_opacity(0.0)
        self.mic_stack.add_named(self.placeholder, "placeholder")

        self.mic_stack.set_visible_child_name("slider" if self.mic_active else "placeholder")
        self.slider_box.pack_start(self.mic_stack, False, False, 0)

    def create_toggle_tile(self, label_text, icon_name, initial_state, callback):
        btn = Gtk.Button()
        btn.get_style_context().add_class("quick-tile")
        if initial_state:
            btn.get_style_context().add_class("active")

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        box.set_margin_start(10)
        box.set_margin_end(10)
        box.set_margin_top(8)
        box.set_margin_bottom(8)

        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
        icon.get_style_context().add_class("tile-icon")

        lbl = Gtk.Label(label=label_text)
        lbl.get_style_context().add_class("tile-label")
        lbl.set_xalign(0)

        box.pack_start(icon, False, False, 0)
        box.pack_start(lbl, True, True, 0)
        btn.add(box)
        btn.connect("clicked", lambda w: callback(btn))
        return btn

    def create_circle_tile(self, label_text, icon_name, initial_state, callback):
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        container.set_halign(Gtk.Align.CENTER)

        btn = Gtk.Button()
        btn.get_style_context().add_class("circle-tile")
        if initial_state:
            btn.get_style_context().add_class("active")

        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DND)
        icon.set_pixel_size(22)
        icon.get_style_context().add_class("circle-icon")
        btn.add(icon)
        btn.connect("clicked", lambda w: callback(btn))

        lbl = Gtk.Label(label=label_text)
        lbl.get_style_context().add_class("circle-label")
        lbl.set_max_width_chars(9)
        lbl.set_ellipsize(3)

        container.pack_start(btn, False, False, 0)
        container.pack_start(lbl, False, False, 0)
        return container

    def create_slider_row(self, icon_name, initial_val, callback):
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row.set_margin_top(0)
        row.set_margin_bottom(0)

        icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
        icon.set_pixel_size(14)
        row.pack_start(icon, False, False, 0)

        scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        scale.set_value(initial_val)
        scale.set_hexpand(True)
        scale.set_draw_value(False)
        scale.connect("value-changed", lambda w: callback(w.get_value()))
        row.pack_start(scale, True, True, 0)
        return row

    def toggle_wifi(self, btn):
        state = get_wifi_state()
        new_state = "off" if state else "on"
        run_cmd(f"nmcli radio wifi {new_state}")
        if not state:
            btn.get_style_context().add_class("active")
        else:
            btn.get_style_context().remove_class("active")
        btn.queue_draw()

    def toggle_bt(self, btn):
        state = get_bt_state()
        if state:
            run_cmd("bluetoothctl power off")
            btn.get_style_context().remove_class("active")
        else:
            run_cmd("rfkill unblock bluetooth && bluetoothctl power on")
            btn.get_style_context().add_class("active")
        btn.queue_draw()

    def toggle_audio_mute(self, btn):
        run_cmd("pamixer -t")
        is_muted = get_audio_mute()
        self.audio_active = not is_muted
        if self.audio_active:
            btn.get_style_context().add_class("active")
        else:
            btn.get_style_context().remove_class("active")
        btn.queue_draw()

    def toggle_mic_view(self, btn):
        run_cmd("pamixer --default-source -t")
        is_muted = get_mic_mute()
        self.mic_active = not is_muted

        target = "slider" if self.mic_active else "placeholder"
        self.mic_stack.set_visible_child_name(target)

        if self.mic_active:
            btn.get_style_context().add_class("active")
        else:
            btn.get_style_context().remove_class("active")
        btn.queue_draw()

    def action_screenshot(self, btn):
        self.cleanup_and_quit()
        run_cmd("hyprshot -m output --clipboard-only")

    def action_settings(self, btn):
        self.cleanup_and_quit()
        run_cmd("gnome-control-center &")

    def on_vol_change(self, val):
        run_cmd(f"pamixer --set-volume {int(val)}")

    def on_mic_change(self, val):
        run_cmd(f"pamixer --default-source --set-volume {int(val)}")

    def on_bright_change(self, val):
        run_cmd(f"brightnessctl set {int(val)}%")

    def cleanup_and_quit(self):
        if os.path.exists(LOCK_FILE):
            try:
                os.remove(LOCK_FILE)
            except OSError:
                pass
        Gtk.main_quit()

    def on_focus_out(self, widget, event):
        self.cleanup_and_quit()
        return False

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            self.cleanup_and_quit()
            return True
        return False

css_provider = Gtk.CssProvider()
css = b"""
window {
    background-color: transparent;
    font-family: "JetBrainsMono Nerd Font", sans-serif;
}
.quicksettings-window {
    background-color: rgba(22, 22, 30, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    padding: 14px;
}

button.quick-tile {
    background-image: none;
    background-color: #141414;
    border: 1px solid #2c2c2c;
    border-radius: 8px;
    outline: none;
    box-shadow: none;
    transition: all 150ms ease;
}
button.quick-tile label.tile-label,
button.quick-tile image.tile-icon {
    color: #ffffff;
}
button.quick-tile:hover {
    background-image: none;
    background-color: #262626;
    border-color: #383838;
}

button.quick-tile.active {
    background-image: none;
    background-color: #ffffff;
    border: 1px solid #ffffff;
    box-shadow: none;
}
button.quick-tile.active label.tile-label,
button.quick-tile.active image.tile-icon {
    color: #141414;
    font-weight: bold;
}
button.quick-tile.active:hover {
    background-image: none;
    background-color: #e5e5e5;
    border-color: #e5e5e5;
}

button.circle-tile {
    background-image: none;
    background-color: #141414;
    border: 1px solid #2c2c2c;
    border-radius: 26px;
    min-width: 52px;
    min-height: 52px;
    outline: none;
    box-shadow: none;
    transition: all 150ms ease;
}
button.circle-tile image.circle-icon {
    color: #ffffff;
}
button.circle-tile:hover {
    background-image: none;
    background-color: #262626;
    border-color: #383838;
}

button.circle-tile.active {
    background-image: none;
    background-color: #ffffff;
    border: 1px solid #ffffff;
}
button.circle-tile.active image.circle-icon {
    color: #141414;
}
button.circle-tile.active:hover {
    background-image: none;
    background-color: #e5e5e5;
    border-color: #e5e5e5;
}

label.circle-label {
    color: #ffffff;
    font-size: 10px;
    font-weight: 500;
}

/* ZERO-HEIGHT SCALE TRACK & THUMB OVERRIDE */
scale {
    margin: 0;
    padding: 0;
    min-height: 0;
}
scale trough {
    background-color: #262626;
    border-radius: 4px;
    min-height: 5px;
    margin: 0;
    padding: 0;
}
scale highlight {
    background-color: #ffffff;
    border-radius: 4px;
}
scale slider {
    background-color: #ffffff;
    border: none;
    border-radius: 50%;
    min-width: 10px;
    min-height: 10px;
    margin: -3px 0;
}
separator {
    background-color: #282828;
}
image {
    color: #ffffff;
}
"""
css_provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(),
    css_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
)

if __name__ == "__main__":
    win = QuickSettings()
    win.connect("destroy", lambda w: win.cleanup_and_quit())
    signal.signal(signal.SIGUSR1, lambda s, f: GLib.idle_add(win.cleanup_and_quit))
    signal.signal(signal.SIGTERM, lambda s, f: GLib.idle_add(win.cleanup_and_quit))
    win.show_all()
    win.mic_stack.set_visible_child_name("slider" if win.mic_active else "placeholder")
    Gtk.main()