#!/usr/bin/env bash
set -e

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}"
LOCAL_BIN="$HOME/.local/bin"

echo "=================================================="
echo " Linking Dotfiles from: $DOTFILES_DIR"
echo " Target config path:    $CONFIG_DIR"
echo "=================================================="

mkdir -p "$CONFIG_DIR"

# 1. Link all folders under .config/
if [ -d "$DOTFILES_DIR/.config" ]; then
    for source_path in "$DOTFILES_DIR/.config"/*; do
        if [ -d "$source_path" ]; then
            name="$(basename "$source_path")"
            target_path="$CONFIG_DIR/$name"

            # If target exists and is a real directory (not symlink), back it up
            if [ -e "$target_path" ] && [ ! -L "$target_path" ]; then
                backup_path="$target_path.backup.$(date +%Y%m%d_%H%M%S)"
                echo "Backing up existing $target_path to $backup_path"
                mv "$target_path" "$backup_path"
            fi

            ln -sfn "$source_path" "$target_path"
            echo "✓ Linked: $target_path -> $source_path"
        fi
    done
fi

# 2. Link binaries under .local/bin/ if present
if [ -d "$DOTFILES_DIR/.local/bin" ]; then
    mkdir -p "$LOCAL_BIN"
    for bin_path in "$DOTFILES_DIR/.local/bin"/*; do
        if [ -f "$bin_path" ]; then
            bin_name="$(basename "$bin_path")"
            target_bin="$LOCAL_BIN/$bin_name"
            ln -sfn "$bin_path" "$target_bin"
            chmod +x "$bin_path" 2>/dev/null || true
            echo "✓ Linked bin: $target_bin -> $bin_path"
        fi
    done
fi

# 3. Link root dotfiles (e.g., .bashrc, .bash_aliases) if present
for dotfile in .bash_aliases .bashrc .bashrcprintf; do
    if [ -f "$DOTFILES_DIR/$dotfile" ]; then
        target_file="$HOME/$dotfile"
        if [ -e "$target_file" ] && [ ! -L "$target_file" ]; then
            backup_file="$target_file.backup.$(date +%Y%m%d_%H%M%S)"
            echo "Backing up existing $target_file to $backup_file"
            mv "$target_file" "$backup_file"
        fi
        ln -sfn "$DOTFILES_DIR/$dotfile" "$target_file"
        echo "✓ Linked root file: $target_file -> $DOTFILES_DIR/$dotfile"
    fi
done

echo "=================================================="
echo " All dotfiles linked successfully!"
echo "=================================================="
