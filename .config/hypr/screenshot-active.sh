#!/usr/bin/env bash

geom=$(hyprctl activewindow -j | jq -r '"\(.at[0]),\(.at[1]) \(.size[0])x\(.size[1])"')
if [ -n "$geom" ] && [ "$geom" != "null,null nullxnull" ]; then
    grim -g "$geom" - | tee "$HOME/Pictures/Screenshots/$(date +%Y-%m-%d_%H-%M-%S).png" | wl-copy -t image/png
fi
