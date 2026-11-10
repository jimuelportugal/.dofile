> [!IMPORTANT]
> ## 🚨 [MUST READ: Repository Documentation & Setup Guide](https://github.com/jimuelportugal/.dofile/issues/9#issue-6308226202)
> *Click above to view the full documentation, installation trace, and setup details.*

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

## 🚀 Universal Installer & Setup

The included installer (`install.sh`) is designed to set up and configure any machine or user account across multiple Linux distributions (Fedora, Arch Linux, Debian/Ubuntu, openSUSE).

### Quick Install:
```bash
git clone https://github.com/jimuelportugal/.dofile.git ~/.dotfiles
cd ~/.dotfiles
./install.sh
```

### Key Capabilities:
* **Multi-Distribution Detection**: Automatically detects package managers (`dnf`, `pacman`, `apt`, `zypper`) and offers to install required dependencies (Hyprland, Waybar, Swaybg, Wob, Pamixer, Brightnessctl, PyGObject, Thunar, etc.).
* **Nerd Font Auto-Provisioning**: Checks for JetBrainsMono Nerd Font and automatically downloads/installs it if missing so icons and glyphs render cleanly.
* **Safe Centralized Backups**: Pre-existing configurations are non-destructively archived into a timestamped directory `~/.dotfiles_backup_<timestamp>/`.
* **Hardware & User Independence**: All configs use dynamic user paths (`$HOME`) and universal display fallback rules (`monitor = , preferred, auto, 1`) to adapt seamlessly across different laptops, desktops, and user accounts.
* **Automatic PATH Configuration**: Ensures `~/.local/bin` is exported to `$PATH` in `.bashrc`.

### Command-Line Options:
| Flag | Description |
| :--- | :--- |
| `./install.sh` | Interactive guided installation |
| `./install.sh -y` / `--yes` | Unattended automated installation (auto-confirm all steps) |
| `./install.sh -n` / `--dry-run` | Preview all actions without modifying the filesystem |
| `./install.sh -l` / `--link-only` | Only update/create configuration symlinks (skip package installs) |
| `./install.sh -d` / `--deps-only` | Only check and install system packages |
| `./install.sh --no-fonts` | Skip Nerd Font check and download |

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

---

## 📁 Repository File Map

### 📦 Tracked

**Shell & Core Configuration:**
* `~/.bashrc`
* `~/.bash_aliases`
* `~/.bashrcprintf`

**Repository & Configuration Switcher CLIs:**
* `~/.local/bin/dotfiles-git` (automated staging, commit, and push manager)
* `~/.local/bin/hypr-lua` (activate modern Lua configuration engine)
* `~/.local/bin/hypr-conf` (activate legacy fallback configuration)
* `~/.local/bin/hypr-status` (check currently active compositor configuration mode)
* `~/.local/bin/thunar-terminal` (POSIX path resolver for context-menu terminal launches)

**Compositor (Hyprland):**
* `~/.config/hypr/hyprland.lua` (primary Lua configuration with GNOME slide animations & input limits)
* `~/.config/hypr/hyprland.conf` (legacy fallback synchronized with Lua parity)
* `~/.config/hypr/wallpaper.jpg`
* `~/.config/hypr/screenshot-active.sh`
* `~/.config/hypr/drawer_pinned.json` (category mapping and priority pins for drawer)

**Compositor Scripts & Launchers:**
* `~/.config/hypr/scripts/drawer.py` (Cairo-curved GTK3 layer-shell app drawer with dynamic XDG discovery and hover arming)
* `~/.config/hypr/scripts/scroll-workspace.sh` (active-only bounded workspace scroll switcher with Lua IPC dispatch)
* `~/.config/hypr/scripts/quicksettings.py` (quick settings control panel)

**File Manager & Desktop Theme (Kali-Dark 1:1):**
* `~/.config/Thunar/uca.xml` (custom context-menu actions: terminal, root edit, search, checksum)
* `~/.config/xfce4/xfconf/xfce-perchannel-xml/thunar.xml` (view preferences, side-pane, and layout)
* `~/.config/gtk-3.0/gtk.css` (Kali-Dark styling, breadcrumb pills, and dark mode palette)
* `~/.config/gtk-3.0/colors.css`
* `~/.config/gtk-3.0/settings.ini`
* `~/.config/gtk-3.0/bookmarks`

**Status Bar (Waybar):**
* `~/.config/waybar/config.jsonc`
* `~/.config/waybar/style.css`
* `~/.config/waybar/menu.xml`
* `~/.config/waybar/rofi-wifi.sh`
* `~/.config/waybar/scripts/slider-popup.py`

**Session Power Menu:**
* `~/.config/wlogout/` (all themes, modern/glass layouts, icons, noise texture, colors)

**Input Method (Fcitx5):**
* `~/.config/fcitx5/config`
* `~/.config/fcitx5/profile`
* `~/.config/fcitx5/conf/cached_layouts`
* `~/.config/fcitx5/conf/notifications.conf`
* `~/.config/fcitx5/conf/wayland.conf`

**Device Remapping (input-remapper-2):**
* `~/.config/input-remapper-2/config.json`
* `~/.config/input-remapper-2/xmodmap.json`
* `~/.config/input-remapper-2/presets/` (all device JSON presets)

**Audio Routing:**
* `~/.config/pipewire/pipewire.conf.d/reverse-audio.conf`

**Launcher Menus:**
* `~/.config/rofi/wifi.rasi`
* `~/.config/nwg-drawer/drawer.css`

---

### ⏳ Untracked (Pending Review & Staging)

**Volume/Brightness Overlay Bar:**
* `~/.config/wob/wob.ini` (OSD styling and dimensions present locally in `~/.config/wob/`, pending repo import)

**Hardware Input Toggle:**
* `~/.config/hypr/scripts/toggle-laptop-inputs.sh` (bound to `SUPER + F6`, pending script implementation)
