#!/usr/bin/env bash
# =============================================================================
# Hyprland Dotfiles Universal Installer & System Configurator
# Supports: Fedora, Arch Linux, Debian/Ubuntu, openSUSE & multi-user systems
# =============================================================================

set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}"
LOCAL_BIN="$HOME/.local/bin"
FONTS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/fonts"
SCREENSHOTS_DIR="$HOME/Pictures/Screenshots"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_DIR="$HOME/.dotfiles_backup_$TIMESTAMP"

# CLI Options
AUTO_YES=false
DRY_RUN=false
DEPS_ONLY=false
LINK_ONLY=false
NO_FONTS=false

# Styling
C_RESET="\033[0m"
C_BOLD="\033[1m"
C_CYAN="\033[36m"
C_GREEN="\033[32m"
C_YELLOW="\033[33m"
C_RED="\033[31m"
C_BLUE="\033[34m"

info()    { echo -e "${C_CYAN}${C_BOLD}[INFO]${C_RESET} $*"; }
success() { echo -e "${C_GREEN}${C_BOLD}[OK]${C_RESET} $*"; }
warn()    { echo -e "${C_YELLOW}${C_BOLD}[WARN]${C_RESET} $*"; }
error()   { echo -e "${C_RED}${C_BOLD}[ERROR]${C_RESET} $*" >&2; }
dry()     { echo -e "${C_BLUE}${C_BOLD}[DRY-RUN]${C_RESET} $*"; }

usage() {
    cat << EOF
${C_BOLD}Hyprland Dotfiles Universal Installer${C_RESET}

Usage: ./install.sh [OPTIONS]

Options:
  -y, --yes          Non-interactive mode (automatically answer YES to all prompts)
  -n, --dry-run      Simulate installation without modifying any files
  -d, --deps-only    Only install system dependencies, do not link configurations
  -l, --link-only    Only link configuration files, skip package dependencies
      --no-fonts     Skip checking and downloading JetBrainsMono Nerd Font
  -h, --help         Show this help message and exit

Examples:
  ./install.sh             # Interactive guided setup
  ./install.sh -y          # Unattended automated setup (new device provisioning)
  ./install.sh -n          # Dry-run preview
  ./install.sh --link-only # Re-apply / sync dotfile symlinks only
EOF
    exit 0
}

# Parse Command Line Arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        -y|--yes)       AUTO_YES=true; shift ;;
        -n|--dry-run)   DRY_RUN=true; shift ;;
        -d|--deps-only) DEPS_ONLY=true; shift ;;
        -l|--link-only) LINK_ONLY=true; shift ;;
        --no-fonts)     NO_FONTS=true; shift ;;
        -h|--help)      usage ;;
        *) error "Unknown option: $1"; usage ;;
    esac
done

ask_confirm() {
    local prompt="$1"
    local default_yes="${2:-true}"
    
    if [ "$AUTO_YES" = true ] || [ "$DRY_RUN" = true ]; then
        return 0
    fi

    if [ "$default_yes" = true ]; then
        read -r -p "$prompt [Y/n]: " response
        case "$response" in
            [nN][oO]|[nN]) return 1 ;;
            *) return 0 ;;
        esac
    else
        read -r -p "$prompt [y/N]: " response
        case "$response" in
            [yY][eE][sS]|[yY]) return 0 ;;
            *) return 1 ;;
        esac
    fi
}

echo -e "${C_BOLD}======================================================${C_RESET}"
echo -e "${C_BOLD}     🚀 Hyprland Dotfiles Setup & Installer           ${C_RESET}"
echo -e "${C_BOLD}======================================================${C_RESET}"
echo -e " User:        ${C_GREEN}$USER${C_RESET} (Home: $HOME)"
echo -e " Source:      $DOTFILES_DIR"
echo -e " Target:      $CONFIG_DIR"
echo -e " Mode:        $([ "$DRY_RUN" = true ] && echo "${C_YELLOW}DRY-RUN${C_RESET}" || echo "${C_GREEN}LIVE${C_RESET}")"
echo -e "======================================================\n"

# -----------------------------------------------------------------------------
# 1. OS & Package Manager Detection
# -----------------------------------------------------------------------------
detect_os() {
    OS_ID="unknown"
    OS_NAME="Linux"
    PKG_MGR="unknown"

    if [ -f /etc/os-release ]; then
        # shellcheck disable=SC1091
        . /etc/os-release
        OS_ID="${ID:-unknown}"
        OS_NAME="${PRETTY_NAME:-$NAME}"
    fi

    if command -v dnf >/dev/null 2>&1; then
        PKG_MGR="dnf"
    elif command -v pacman >/dev/null 2>&1; then
        PKG_MGR="pacman"
    elif command -v apt-get >/dev/null 2>&1; then
        PKG_MGR="apt"
    elif command -v zypper >/dev/null 2>&1; then
        PKG_MGR="zypper"
    fi

    info "Detected OS: ${C_BOLD}$OS_NAME${C_RESET} (Package Manager: ${C_GREEN}$PKG_MGR${C_RESET})"
}

# -----------------------------------------------------------------------------
# 2. Dependency Checking & Installation
# -----------------------------------------------------------------------------
install_dependencies() {
    if [ "$LINK_ONLY" = true ]; then
        info "Skipping dependency installation (--link-only)."
        return 0
    fi

    info "Checking required system packages..."

    # Define core tools to check
    local CORE_CMDS=(
        "Hyprland" "waybar" "swaybg" "thunar" "ptyxis"
        "pamixer" "brightnessctl" "wob" "grim" "slurp"
        "wl-copy" "jq" "python3" "nm-applet" "blueman-manager"
    )

    local MISSING_CMDS=()
    for cmd in "${CORE_CMDS[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            MISSING_CMDS+=("$cmd")
        fi
    done

    # Check PyGObject (Gtk & GtkLayerShell) for drawer.py & slider-popup.py
    local HAS_PY_GI=true
    if ! python3 -c "import gi; gi.require_version('Gtk', '3.0'); gi.require_version('GtkLayerShell', '0.1'); from gi.repository import Gtk, GtkLayerShell" >/dev/null 2>&1; then
        HAS_PY_GI=false
        MISSING_CMDS+=("gtk-layer-shell (PyGObject)")
    fi

    if [ ${#MISSING_CMDS[@]} -eq 0 ]; then
        success "All core dependencies and PyGObject bindings are installed!"
        return 0
    fi

    warn "The following packages or capabilities appear to be missing:"
    for m in "${MISSING_CMDS[@]}"; do
        echo -e "   • ${C_YELLOW}$m${C_RESET}"
    done
    echo ""

    if [ "$PKG_MGR" = "unknown" ]; then
        warn "Could not determine system package manager. Please install the missing tools manually."
        return 0
    fi

    if ! ask_confirm "Would you like to install missing system packages automatically using $PKG_MGR?" true; then
        warn "Skipping automated package installation per user request."
        return 0
    fi

    local PKGS_TO_INSTALL=()
    case "$PKG_MGR" in
        dnf)
            PKGS_TO_INSTALL=(
                hyprland xdg-desktop-portal-hyprland
                waybar swaybg wob pamixer brightnessctl
                ptyxis thunar thunar-archive-plugin thunar-volman
                grim slurp wl-clipboard jq
                gtk-layer-shell gtk-layer-shell-devel python3-gobject
                NetworkManager-applet blueman wlogout
            )
            info "Running: sudo dnf install -y ${PKGS_TO_INSTALL[*]}"
            if [ "$DRY_RUN" = false ]; then
                sudo dnf install -y "${PKGS_TO_INSTALL[@]}" || warn "Some packages failed to install, continuing..."
            else
                dry "sudo dnf install -y ${PKGS_TO_INSTALL[*]}"
            fi
            ;;
        pacman)
            PKGS_TO_INSTALL=(
                hyprland xdg-desktop-portal-hyprland
                waybar swaybg wob pamixer brightnessctl
                thunar thunar-archive-plugin thunar-volman
                grim slurp wl-clipboard jq
                gtk-layer-shell python-gobject
                network-manager-applet blueman
            )
            # Try to install ptyxis or fallback terminal
            if pacman -Si ptyxis >/dev/null 2>&1; then
                PKGS_TO_INSTALL+=(ptyxis)
            else
                PKGS_TO_INSTALL+=(kitty)
            fi

            info "Running: sudo pacman -S --needed --noconfirm ${PKGS_TO_INSTALL[*]}"
            if [ "$DRY_RUN" = false ]; then
                sudo pacman -S --needed --noconfirm "${PKGS_TO_INSTALL[@]}" || warn "Some packages failed to install, continuing..."
            else
                dry "sudo pacman -S --needed --noconfirm ${PKGS_TO_INSTALL[*]}"
            fi
            ;;
        apt)
            PKGS_TO_INSTALL=(
                waybar swaybg wob pamixer brightnessctl
                thunar thunar-archive-plugin
                grim slurp wl-clipboard jq
                libgtk-layer-shell0 libgtk-layer-shell-dev gir1.2-gtklayershell-0.1 python3-gi
                network-manager-gnome blueman
            )
            info "Running: sudo apt-get update && sudo apt-get install -y ${PKGS_TO_INSTALL[*]}"
            if [ "$DRY_RUN" = false ]; then
                sudo apt-get update && sudo apt-get install -y "${PKGS_TO_INSTALL[@]}" || warn "Some packages failed to install, continuing..."
            else
                dry "sudo apt-get update && sudo apt-get install -y ${PKGS_TO_INSTALL[*]}"
            fi
            ;;
        zypper)
            PKGS_TO_INSTALL=(
                hyprland waybar swaybg wob pamixer brightnessctl
                thunar thunar-volman grim slurp wl-clipboard jq
                gtk-layer-shell-devel python3-gobject
                NetworkManager-applet blueman
            )
            info "Running: sudo zypper install -y --no-recommends ${PKGS_TO_INSTALL[*]}"
            if [ "$DRY_RUN" = false ]; then
                sudo zypper install -y --no-recommends "${PKGS_TO_INSTALL[@]}" || warn "Some packages failed to install, continuing..."
            else
                dry "sudo zypper install -y --no-recommends ${PKGS_TO_INSTALL[*]}"
            fi
            ;;
    esac

    success "Package installation step finished."
}

# -----------------------------------------------------------------------------
# 3. Nerd Font Setup (JetBrainsMono Nerd Font)
# -----------------------------------------------------------------------------
setup_nerd_font() {
    if [ "$NO_FONTS" = true ] || [ "$DEPS_ONLY" = true ]; then
        return 0
    fi

    info "Checking for installed Nerd Fonts..."
    if fc-list : family 2>/dev/null | grep -iq "Nerd Font"; then
        success "Nerd Font detected! (Waybar, Terminal, and Drawer icons will display correctly)"
        return 0
    fi

    warn "No Nerd Font detected. System icons may render as empty squares [□]."
    if ! ask_confirm "Download and install JetBrainsMono Nerd Font to $FONTS_DIR?" true; then
        return 0
    fi

    local FONT_URL="https://github.com/ryanoasis/nerd-fonts/releases/latest/download/JetBrainsMono.tar.xz"
    local TARGET_DIR="$FONTS_DIR/JetBrainsMonoNerd"

    if [ "$DRY_RUN" = true ]; then
        dry "mkdir -p '$TARGET_DIR' && curl -sL '$FONT_URL' | tar -xJ -C '$TARGET_DIR' && fc-cache -f"
        return 0
    fi

    if ! mkdir -p "$TARGET_DIR" 2>/dev/null; then
        warn "Could not create '$TARGET_DIR' (check filesystem permissions). Skipping font download."
        return 0
    fi
    info "Downloading JetBrainsMono Nerd Font from GitHub..."
    if command -v curl >/dev/null 2>&1; then
        curl -fSL "$FONT_URL" -o /tmp/JetBrainsMono.tar.xz
    elif command -v wget >/dev/null 2>&1; then
        wget -q "$FONT_URL" -O /tmp/JetBrainsMono.tar.xz
    else
        warn "Neither curl nor wget found. Skipping font download."
        return 0
    fi

    tar -xJf /tmp/JetBrainsMono.tar.xz -C "$TARGET_DIR" 2>/dev/null || true
    rm -f /tmp/JetBrainsMono.tar.xz

    if command -v fc-cache >/dev/null 2>&1; then
        fc-cache -f "$FONTS_DIR"
    fi
    success "JetBrainsMono Nerd Font installed successfully!"
}

# -----------------------------------------------------------------------------
# 4. Environment & Directory Preparation
# -----------------------------------------------------------------------------
prepare_directories() {
    info "Ensuring standard directories exist..."
    local DIRS=(
        "$CONFIG_DIR"
        "$LOCAL_BIN"
        "$SCREENSHOTS_DIR"
        "$FONTS_DIR"
    )

    for dir in "${DIRS[@]}"; do
        if [ "$DRY_RUN" = true ]; then
            dry "mkdir -p '$dir'"
        else
            mkdir -p "$dir" 2>/dev/null || true
        fi
    done
    success "Directory structure ready."
}

# -----------------------------------------------------------------------------
# 5. Backup & Symlinking Core Dotfiles
# -----------------------------------------------------------------------------
backup_and_link() {
    local source="$1"
    local target="$2"
    local label="$3"

    if [ ! -e "$source" ]; then
        return 0
    fi

    # Check if target already points to our repository source
    if [ -L "$target" ]; then
        local current_dest
        current_dest="$(readlink -f "$target" 2>/dev/null || true)"
        local expected_dest
        expected_dest="$(readlink -f "$source" 2>/dev/null || true)"
        if [ "$current_dest" = "$expected_dest" ]; then
            success "Already linked: $label"
            return 0
        fi
    fi

    # If target exists and is not our symlink, safely back it up
    if [ -e "$target" ] || [ -L "$target" ]; then
        if [ "$DRY_RUN" = true ]; then
            dry "Backup: $target -> $BACKUP_DIR/"
        else
            mkdir -p "$BACKUP_DIR" 2>/dev/null || true
            local rel_target="${target#$HOME/}"
            local dest_backup="$BACKUP_DIR/$rel_target"
            mkdir -p "$(dirname "$dest_backup")" 2>/dev/null || true
            if mv "$target" "$dest_backup" 2>/dev/null; then
                warn "Backed up existing $label to $dest_backup"
            else
                warn "Could not back up existing $label (permission denied or read-only)"
            fi
        fi
    fi

    # Create parent folder if missing and establish symbolic link
    if [ "$DRY_RUN" = true ]; then
        dry "ln -sfn '$source' '$target'"
    else
        mkdir -p "$(dirname "$target")" 2>/dev/null || true
        if ln -sfn "$source" "$target" 2>/dev/null; then
            success "Linked $label -> $target"
        else
            warn "Could not link $label -> $target (permission denied or read-only)"
        fi
    fi
}

apply_dotfiles() {
    if [ "$DEPS_ONLY" = true ]; then
        info "Skipping dotfile linking (--deps-only)."
        return 0
    fi

    info "Linking dotfiles and configurations..."

    # 1. Link every module folder in .config/
    if [ -d "$DOTFILES_DIR/.config" ]; then
        for item in "$DOTFILES_DIR/.config"/*; do
            if [ -d "$item" ]; then
                local mod_name
                mod_name="$(basename "$item")"
                backup_and_link "$item" "$CONFIG_DIR/$mod_name" ".config/$mod_name"
            fi
        done
    fi

    # 2. Link helper binaries in .local/bin/
    if [ -d "$DOTFILES_DIR/.local/bin" ]; then
        for bin_file in "$DOTFILES_DIR/.local/bin"/*; do
            if [ -f "$bin_file" ]; then
                local bin_name
                bin_name="$(basename "$bin_file")"
                backup_and_link "$bin_file" "$LOCAL_BIN/$bin_name" ".local/bin/$bin_name"
                [ "$DRY_RUN" = false ] && chmod +x "$bin_file" "$LOCAL_BIN/$bin_name" 2>/dev/null || true
            fi
        done
    fi

    # 3. Link root shell files (.bashrc, .bash_aliases, .bashrcprintf)
    for root_file in .bash_aliases .bashrc .bashrcprintf; do
        if [ -f "$DOTFILES_DIR/$root_file" ]; then
            backup_and_link "$DOTFILES_DIR/$root_file" "$HOME/$root_file" "$root_file"
        fi
    done

    # 4. Ensure scripts are executable
    if [ "$DRY_RUN" = false ]; then
        find "$DOTFILES_DIR/.config/hypr/scripts" -type f -name "*.py" -o -name "*.sh" 2>/dev/null | while read -r script; do
            chmod +x "$script" 2>/dev/null || true
        done
        chmod +x "$DOTFILES_DIR/.config/waybar/scripts/"*.py 2>/dev/null || true
        chmod +x "$DOTFILES_DIR/.config/waybar/rofi-wifi.sh" 2>/dev/null || true
    fi

    # 5. Ensure ~/.local/bin is permanently in user's PATH
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        info "Adding $HOME/.local/bin to PATH in ~/.bashrc..."
        if [ "$DRY_RUN" = false ]; then
            if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc" 2>/dev/null; then
                echo -e '\n# User local binaries\nexport PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
            fi
        else
            dry "Append 'export PATH=\"\$HOME/.local/bin:\$PATH\"' to ~/.bashrc"
        fi
    fi
}

# -----------------------------------------------------------------------------
# 6. Verification & Session Reload
# -----------------------------------------------------------------------------
verify_and_reload() {
    if [ "$DRY_RUN" = true ] || [ "$DEPS_ONLY" = true ]; then
        return 0
    fi

    echo ""
    info "Verifying Hyprland configuration..."
    if command -v Hyprland >/dev/null 2>&1; then
        if Hyprland --verify-config >/dev/null 2>&1; then
            success "Hyprland configuration syntax check PASSED!"
        else
            warn "Hyprland syntax check returned a warning. Run 'Hyprland --verify-config' for details."
        fi
    fi

    # If running inside active Hyprland session, offer to reload live
    if [ -n "${HYPRLAND_INSTANCE_SIGNATURE:-}" ] || pgrep -x Hyprland >/dev/null 2>&1; then
        if ask_confirm "Active Hyprland session detected. Reload Hyprland live now?" true; then
            hyprctl reload || true
            command -v notify-send >/dev/null 2>&1 && notify-send "Hyprland Dotfiles" "Configuration reloaded successfully!" -u low || true
            success "Hyprland reloaded!"
        fi
    fi
}

# -----------------------------------------------------------------------------
# Main Execution Flow
# -----------------------------------------------------------------------------
main() {
    detect_os
    prepare_directories
    install_dependencies
    setup_nerd_font
    apply_dotfiles
    verify_and_reload

    echo ""
    echo -e "${C_BOLD}======================================================${C_RESET}"
    echo -e "${C_GREEN}${C_BOLD} 🎉 Setup Complete!                                   ${C_RESET}"
    echo -e "${C_BOLD}======================================================${C_RESET}"
    if [ -d "$BACKUP_DIR" ]; then
        echo -e " 📁 Any pre-existing files were backed up safely to:"
        echo -e "    ${C_CYAN}$BACKUP_DIR${C_RESET}"
    fi
    echo -e " 💡 Quick Switchers:"
    echo -e "    • ${C_YELLOW}hypr-lua${C_RESET}    -> Switch to modern Lua configuration"
    echo -e "    • ${C_YELLOW}hypr-conf${C_RESET}   -> Switch to legacy conf configuration"
    echo -e "    • ${C_YELLOW}hypr-status${C_RESET} -> View active configuration status"
    echo -e "    • ${C_YELLOW}dotfiles-git${C_RESET}-> Sync and manage dotfiles repository"
    echo -e "======================================================\n"
}

main
