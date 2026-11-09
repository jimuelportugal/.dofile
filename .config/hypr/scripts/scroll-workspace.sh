#!/usr/bin/env bash
# Non-wrapping workspace scrolling for OPEN/USED workspaces only
# Usage: scroll-workspace.sh [+1|-1|down|up]

dir="$1"

# Query active workspace ID
active_id=$(hyprctl activeworkspace -j 2>/dev/null | jq -r '.id')
[ -z "$active_id" ] && exit 0

# Query sorted list of all active positive workspace IDs (excluding special workspaces)
mapfile -t workspaces < <(hyprctl workspaces -j 2>/dev/null | jq -r '[.[] | select(.id > 0) | .id] | sort | .[]')
[ "${#workspaces[@]}" -le 1 ] && exit 0

# Find current index
current_idx=-1
for i in "${!workspaces[@]}"; do
    if [ "${workspaces[$i]}" -eq "$active_id" ]; then
        current_idx=$i
        break
    fi
done

target_id=""

if [ "$current_idx" -ge 0 ]; then
    # Currently on an active workspace: move to adjacent active workspace without wrap
    if [ "$dir" = "+1" ] || [ "$dir" = "down" ]; then
        target_idx=$((current_idx + 1))
        [ "$target_idx" -ge "${#workspaces[@]}" ] && exit 0
    elif [ "$dir" = "-1" ] || [ "$dir" = "up" ]; then
        target_idx=$((current_idx - 1))
        [ "$target_idx" -lt 0 ] && exit 0
    else
        exit 0
    fi
    target_id="${workspaces[$target_idx]}"
else
    # Currently on an empty/untracked workspace: jump to the nearest active one
    if [ "$dir" = "+1" ] || [ "$dir" = "down" ]; then
        for ws in "${workspaces[@]}"; do
            if [ "$ws" -gt "$active_id" ]; then
                target_id="$ws"
                break
            fi
        done
        [ -z "$target_id" ] && exit 0
    elif [ "$dir" = "-1" ] || [ "$dir" = "up" ]; then
        for ws in "${workspaces[@]}"; do
            if [ "$ws" -lt "$active_id" ]; then
                target_id="$ws"
            fi
        done
        [ -z "$target_id" ] && exit 0
    else
        exit 0
    fi
fi

if [ -n "$target_id" ] && [ "$target_id" -ne "$active_id" ]; then
    # Support both Hyprland Lua config (hl.dsp.focus) and legacy conf (workspace N)
    hyprctl dispatch "hl.dsp.focus({ workspace = $target_id })" 2>/dev/null || hyprctl dispatch workspace "$target_id"
fi

