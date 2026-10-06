#!/usr/bin/env python3
import sys
import subprocess
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('GtkLayerShell', '0.1')
from gi.repository import Gtk, Gdk, GtkLayerShell

mode = sys.argv[1] if len(sys.argv) > 1 else "volume"

def get_volume():
    try:
        out = subprocess.check_output(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"]).decode()
        parts = out.strip().split()
        return int(float(parts[1]) * 100) if len(parts) >= 2 else 50
    except Exception:
        return 50

def get_brightness():
    try:
        cur = subprocess.check_output(["brightnessctl", "g"]).decode().strip()
        mx = subprocess.check_output(["brightnessctl", "m"]).decode().strip()
        return int((int(cur) / int(mx)) * 100)
    except Exception:
        return 50

val = get_volume() if mode == "volume" else get_brightness()

win = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
win.set_title(f"popup-{mode}")
win.set_decorated(False)

# Layer shell setup
GtkLayerShell.init_for_window(win)
GtkLayerShell.set_layer(win, GtkLayerShell.Layer.OVERLAY)
GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.TOP, True)
GtkLayerShell.set_anchor(win, GtkLayerShell.Edge.RIGHT, True)
GtkLayerShell.set_margin(win, GtkLayerShell.Edge.TOP, -1)
# Adjust position under backlight or pulseaudio
GtkLayerShell.set_margin(win, GtkLayerShell.Edge.RIGHT, 35 if mode == "volume" else 85)
GtkLayerShell.set_keyboard_mode(win, GtkLayerShell.KeyboardMode.ON_DEMAND)

# Dismiss on focus loss or Escape key
win.connect("focus-out-event", lambda w, e: Gtk.main_quit())
def on_key(w, e):
    if e.keyval == Gdk.KEY_Escape:
        Gtk.main_quit()
win.connect("key-press-event", on_key)

# Container
frame = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
frame.set_size_request(240, 36)
frame.set_margin_start(14)
frame.set_margin_end(14)
frame.set_margin_top(8)
frame.set_margin_bottom(8)

# Icon indicator
icon_label = Gtk.Label(label="" if mode == "volume" else "")
icon_label.get_style_context().add_class("popup-icon")
frame.pack_start(icon_label, False, False, 0)

# Slider
adj = Gtk.Adjustment(value=val, lower=0, upper=100, step_increment=1, page_increment=5)
scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=adj)
scale.set_hexpand(True)
scale.set_draw_value(False)

def on_change(widget):
    v = int(widget.get_value())
    if mode == "volume":
        subprocess.run(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", f"{v}%"])
    else:
        subprocess.run(["brightnessctl", "set", f"{v}%"])

scale.connect("value-changed", on_change)
frame.pack_start(scale, True, True, 0)

# Percentage label
pct_label = Gtk.Label(label=f"{val}%")
pct_label.set_width_chars(4)
pct_label.get_style_context().add_class("popup-pct")
frame.pack_end(pct_label, False, False, 0)

def update_label(widget):
    pct_label.set_text(f"{int(widget.get_value())}%")
scale.connect("value-changed", update_label)

win.add(frame)

# CSS Styling matching your theme
css = b"""
window {
    background-color: rgba(14, 10, 20, 0.95);
    border: none;
    border-radius: 50px;
}
.popup-icon {
    color: #ff2a85;
    font-size: 14px;
}
.popup-pct {
    color: #f8f8fc;
    font-size: 12px;
    font-family: monospace;
}
scale trough {
    background-color: #221630;
    border-radius: 6px;
    min-height: 8px;
}
scale highlight {
    background-color: #ff2a85;
    border-radius: 5px;
}
scale slider {
    background-color: #ffffff;
    border-radius: 50%;
    min-width: 16px;
    min-height: 10px;
}
"""
provider = Gtk.CssProvider()
provider.load_from_data(css)
Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

win.show_all()
Gtk.main()
