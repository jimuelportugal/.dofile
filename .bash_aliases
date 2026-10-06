# YTDLP CLI tool
alias yt='~/PROGRAMMING/python/YTDLP/YTDLP.sh'

alias repo-update='git add . && git commit -m "update" && git push'

# SCRPY control for lenovo tab M11
alias lenovo-control='/home/irys/PROGRAMMING/scrcpy-linux-x86_64-v3.3.4/scrcpy --otg -s HA1Z5AST'
alias lenovo-draw='adb reverse tcp:1701 tcp:1701 && adb reverse tcp:9001 tcp:9001'

# VS CODE config shortcut
alias tconfig='code ~/.bashrc'
alias aconfig='code ~/.bash_aliases'

# Steam/Wine Game runner
forgotten() {
    cd "$HOME/.steam/steam/steamapps/common/Kenshi" || return
    wine "forgotten construction set.exe"
}

# CUPS PRINTING SERVICE
alias print-enable='sudo systemctl unmask cups.service cups.socket cups.path && sudo systemctl start cups.service cups.socket cups.path && echo "CUPS enabled."'
alias print-disable='sudo systemctl mask --now cups.service cups.socket cups.path && echo "CUPS disabled and masked."'

# Network & IP Utilities
ipconfig() {
    ip -br a
    echo -n "LOCAL  : " && hostname -I | awk '{print $1}'
}
alias localip="hostname -I | awk '{print \$1}'"
alias pubip='curl -s ifconfig.me; echo'
alias nmsr='sudo systemctl restart systemd-resolved'
alias dnsflush='sudo resolvectl flush-caches && sudo resolvectl statistics'

# WGET
alias gowget='wget -c --tries=0 --retry-connrefused --waitretry=5'
gwget() {
    if [ -z "$1" ]; then
        echo "Usage: gwget <URL> [output_filename]"
        return 1
    fi
    if [ -n "$2" ]; then
        wget -c --tries=0 --retry-connrefused --waitretry=5 -O "$2" "$1"
    else
        wget -c --tries=0 --retry-connrefused --waitretry=5 "$1"
    fi
}

# LAPTOP KEYBOARD TOGGLE
toggle-kbd() {
    local node="/sys/devices/platform/i8042/serio0/input/input2/inhibited"
    if [ ! -f "$node" ]; then
        echo "Error: Device node not found." >&2
        return 1
    fi

    local state
    state=$(cat "$node")

    if [ "$state" -eq 0 ]; then
        echo 1 | sudo tee "$node" > /dev/null
        echo "Laptop keyboard: DISABLED"
    else
        echo 0 | sudo tee "$node" > /dev/null
        echo "Laptop keyboard: ENABLED"
    fi
}

# Terminal Refresh
alias trefresh='source ~/.bashrc'

mendou() {
    echo "tconfig        : Open ~/.bashrc in VS CODE"
    echo "aconfig        : Open ~/.bash_aliases in VS CODE"
    echo "trefresh       : Reload bash configuration"
    echo "print-enable   : Start and unmask CUPS service"
    echo "print-disable  : Stop and mask CUPS service"
    echo "yt             : Launch YTDLP script"
    echo "lenovo-control : Launch scrcpy for Lenovo Tab M11"
    echo "lenovo-draw    : Enable reverse TCP ports for tablet drawing"
    echo "dnsflush       : Flush systemd resolved DNS cache"
    echo "nmsr           : Restart systemd-resolved"
    echo "lf             : Search files in current path"
    echo "lfc            : Search files in current path and open in VS Code"
}

# Search helpers
lf() {
    find . -type f -iname "*$1*"
}
lfc() {
    find . -type f -iname "*$1*" -exec code {} +
}

# Source extra format file if present

alias dotfiles='/usr/bin/git --git-dir=$HOME/.dotfiles/ --work-tree=$HOME'
