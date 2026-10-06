# ~/.bashrc: executed by bash(1) for non-login shells.

# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# History settings
HISTCONTROL=ignoreboth
shopt -s histappend
HISTSIZE=1000
HISTFILESIZE=2000

# Update window size after each command
shopt -s checkwinsize

# Friendly less for non-text input files
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# Color support for ls and grep
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# Standard ls aliases
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

# Alert alias for long running commands (e.g. sleep 10; alert)
alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

# Source separate alias definitions
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# Enable programmable completion
if ! shopt -oq posix; then
  if [ -f /usr/share/bash-completion/bash_completion ]; then
    . /usr/share/bash-completion/bash_completion
  elif [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
  fi
fi

# Banner & System Info
echo -e "\e[1;32m"
cat << 'EOF'
    __  __________   ______  ____  __  __   ____  _______    __
   /  |/  / ____/ | / / __ \/ __ \/ / / /  / __ \/ ____/ |  / /
  / /|_/ / __/ /  |/ / / / / / / / / / /  / / / / __/  | | / / 
 / /  / / /___/ /|  / /_/ / /_/ / /_/ /  / /_/ / /___  | |/ /  
/_/  /_/_____/_/ |_/_____/\____/\____/  /_____/_____/  |___/   
EOF
echo -e "\e[0m"

if command -v fastfetch &> /dev/null; then
    fastfetch
fi

# Kali-style two-line prompt
PS1="\[\e[1;36m\]┌──(\[\e[1;38;5;33m\]\u㉿\h\[\e[1;36m\])-[\[\e[0m\]\w\[\e[1;36m\]]\n\[\e[1;36m\]└─\[\e[1;38;5;33m\]$ \[\e[0m\]"

# Environment Paths
export PATH="$HOME/.local/bin:$HOME/bin:$PATH"

# Android SDK
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/emulator:$ANDROID_HOME/platform-tools:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"

# Go Workspace
export GOPATH="$HOME/go"
export PATH="$GOPATH/bin:$PATH"

# Flutter SDK
if [ -d "$HOME/flutter/bin" ]; then
    export PATH="$HOME/flutter/bin:$PATH"
elif [ -d "$HOME/development/flutter/bin" ]; then
    export PATH="$HOME/development/flutter/bin:$PATH"
fi