# MENDOU

Personal dotfiles managed via a Git bare repository targeting `$HOME`.

> **Note:** This is my first Linux rice. Everything is tailored strictly to my personal preferences, hardware, and day-to-day workflow rather than a generic or commercial desktop setup. An auto-installer script will be added in the future.

---

## Tracked Components

- **Compositor:** Hyprland (`.config/hypr`)
- **Status Bar:** Waybar (`.config/waybar`)
- **Input Method:** Fcitx5 (`.config/fcitx5`)
- **Key Remapping:** input-remapper-2 (`.config/input-remapper-2`)
- **Session Menu:** wlogout (`.config/wlogout`)
- **App Launcher / Menus:** Rofi (`.config/rofi`)
- **Audio Routing:** PipeWire (`.config/pipewire`)
- **Shell Environment:** Bash (`.bashrc`, `.bash_aliases`, `.bashrcprintf`)
- **CLI Helper:** `dotfiles-git` (`.local/bin/dotfiles-git`)

---

## Workflow (`dotfiles-git`)

A custom wrapper located at `~/.local/bin/dotfiles-git` automates path resolution and bare Git operations against `$HOME`:

```bash
# Check status from any directory
dotfiles-git status

# Pre-stage core paths and commit
dotfiles-git commit -m "your message"

# Push to remote (auto-stages modified core paths and the helper script)
dotfiles-git push -u origin main

# Add new configs relative to $HOME
dotfiles-git add ~/.config/path/to/file
```
