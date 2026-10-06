#!/usr/bin/env bash

# Fetch cached networks instantly (no scan delay)
get_wifi_list() {
    echo "󰑐  Rescan Networks"
    nmcli --fields "SECURITY,BARS,SSID" device wifi list --rescan no | sed 1d | sed -E "s/  +/ /g" | sed -E "s/^ //g"
}

# Run wofi with auto-dismiss on unfocus
chosen=$(get_wifi_list | wofi --dmenu -i -p "Select Wi-Fi" --hide-scroll)

if [ -z "$chosen" ]; then
    exit 0
fi

# Manual rescan option
if [[ "$chosen" =~ "Rescan Networks" ]]; then
    notify-send "Wi-Fi" "Scanning available networks..." -t 1200 2>/dev/null
    nmcli device wifi list --rescan yes >/dev/null 2>&1
    exec "$0"
    exit 0
fi

# Extract SSID
chosen_id=$(echo "$chosen" | awk '{print substr($0, index($0,$3))}')

# Connect logic
saved_connections=$(nmcli -g NAME connection)
if echo "$saved_connections" | grep -qx "$chosen_id"; then
    nmcli connection up id "$chosen_id"
else
    if echo "$chosen" | grep -qv -- "--"; then
        wifi_password=$(wofi --dmenu --password -p "Enter Password for $chosen_id" --hide-scroll)
        [ -n "$wifi_password" ] && nmcli device wifi connect "$chosen_id" password "$wifi_password"
    else
        nmcli device wifi connect "$chosen_id"
    fi
fi
