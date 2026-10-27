# Dotfiles - Fedora Hyprland

Personal dotfiles and Wayland desktop environment setup for **Fedora Linux** using **Hyprland**, **Waybar**, and custom **GTK Layer-Shell** widgets.

---

## 📂 Repository Structure

Matches the standard `$HOME` hierarchy:

```text
.
├── .config/
│   ├── fcitx5/              # Input method configs (Mozc + US ANSI)
│   ├── gtk-3.0/             # Dark theme settings & custom CSS
│   ├── hypr/                # Hyprland window manager & custom Python scripts
│   │   ├── hyprland.conf
│   │   ├── screenshot-active.sh
│   │   ├── wallpaper.jpg
│   │   └── scripts/
│   │       ├── drawer.py          # Custom GTK Layer-Shell App Drawer
│   │       └── quicksettings.py   # Custom GTK Layer-Shell Quick Settings
│   ├── input-remapper-2/    # Key & mouse remapping presets
│   ├── nwg-drawer/          # Drawer styles
│   ├── pipewire/            # PipeWire reverse-audio configuration
│   ├── rofi/                # Wi-Fi menu styling (wifi.rasi)
│   ├── waybar/              # 3-capsule Waybar layout, scripts & styles
│   └── wlogout/             # Lock/Logout/Suspend overlay menu themes & icons
├── .local/
│   └── bin/                 # User scripts (e.g. dotfiles-git)
├── install.sh               # Automated symlink installer for fresh setups
└── README.md
```

---

## 🚀 Quick Setup / Installation

To link these configurations to `~/.config/` on a new machine:

```bash
git clone https://github.com/<your-username>/<your-repo>.git ~/PROGRAMMING/dotfiles_config
cd ~/PROGRAMMING/dotfiles_config
./install.sh
```

The script will automatically back up any existing folders in `~/.config/` and create symbolic links pointing back to this repository.

---

## ⌨️ Keybindings

| Keybinding | Action |
| :--- | :--- |
| `Super + A` | Open Custom App Drawer (`drawer.py`) |
| `Super + S` | Open Quick Settings Panel (`quicksettings.py`) |
| `Super + C` | VS Code |
| `Super + B` | Brave Browser |
| `Super + G` | Steam |
| `Super + E` | Thunar File Manager |
| `Super + I` | GNOME Control Center |
| `Ctrl + Alt + T` | Terminal (Ptyxis) |
| `Super + Shift + Esc` | Process Monitor (`btop`) |
| `Ctrl + Shift + Alt + B` | Reload Waybar |
| `Super + Q` | Close Active Window |
| `Super + F11` | Toggle Floating Window |
