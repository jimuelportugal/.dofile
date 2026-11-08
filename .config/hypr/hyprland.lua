-- =============================================================================
-- Hyprland Modern Configuration (Lua Format)
-- Converted from hyprland.conf for Hyprland v0.55+ / v0.56+
-- =============================================================================

--------------------------------------------------------------------------------
-- 1. MONITORS
--------------------------------------------------------------------------------
-- See https://wiki.hypr.land/configuring/core/monitors/
hl.monitor({
    output   = "eDP-1",
    mode     = "preferred",
    position = "auto",
    scale    = 1,
})

--------------------------------------------------------------------------------
-- 2. VARIABLES & DEFAULT PROGRAMS
--------------------------------------------------------------------------------
local terminal = "ptyxis"
local menu     = "nwg-drawer -c 6 -is 36 -k -ov"
local mainMod  = "SUPER"

--------------------------------------------------------------------------------
-- 3. ENVIRONMENT VARIABLES
--------------------------------------------------------------------------------
hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")

--------------------------------------------------------------------------------
-- 4. AUTOSTART (EXEC-ONCE)
--------------------------------------------------------------------------------
-- Autostart background processes and daemons on launch
hl.on("hyprland.start", function()
    hl.exec_cmd("waybar")
    hl.exec_cmd("swaybg -i ~/.config/hypr/wallpaper.jpg -m fill")
    hl.exec_cmd("nm-applet --indicator")
    hl.exec_cmd("/usr/libexec/lxqt-policykit-agent")
    hl.exec_cmd("gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark'")
    hl.exec_cmd("sh -c 'rm -f $XDG_RUNTIME_DIR/wob.sock && mkfifo $XDG_RUNTIME_DIR/wob.sock && tail -f $XDG_RUNTIME_DIR/wob.sock | wob'")
    hl.exec_cmd("blueman-applet")
end)

--------------------------------------------------------------------------------
-- 5. INPUT & DEVICES
--------------------------------------------------------------------------------
-- Input configuration (keyboard layout, mouse sensitivity, touchpad gestures)
hl.config({
    input = {
        kb_layout = "us",
        follow_mouse = 1,
        touchpad = {
            natural_scroll = false,
        },
        sensitivity = 0,
    },
})

--------------------------------------------------------------------------------
-- 6. GENERAL (LAYOUT & BORDERS)
--------------------------------------------------------------------------------
hl.config({
    general = {
        gaps_in  = 4,
        gaps_out = 8,
        border_size = 0,
        col = {
            active_border   = "rgba(332d41ee)",
            inactive_border = "rgba(221630aa)",
        },
        resize_on_border     = true,
        hover_icon_on_border = true,
        layout               = "dwindle",
    },
})

--------------------------------------------------------------------------------
-- 7. DECORATION (ROUNDING, OPACITY, BLUR)
--------------------------------------------------------------------------------
hl.config({
    decoration = {
        rounding         = 10,
        active_opacity   = 1.0,
        inactive_opacity = 0.75,
        blur = {
            enabled = true,
            size    = 10,
            passes  = 2,
        },
    },
})

--------------------------------------------------------------------------------
-- 8. ANIMATIONS & CURVES
--------------------------------------------------------------------------------
hl.config({
    animations = {
        enabled = true,
    },
})

-- Bezier curves and spring definitions
hl.curve("easeOutQuint",   { type = "bezier", points = { {0.23, 1},    {0.32, 1}    } })
hl.curve("easeInOutCubic", { type = "bezier", points = { {0.65, 0.05}, {0.36, 1}    } })
hl.curve("linear",         { type = "bezier", points = { {0, 0},       {1, 1}       } })
hl.curve("almostLinear",   { type = "bezier", points = { {0.5, 0.5},   {0.75, 1}    } })
hl.curve("quick",          { type = "bezier", points = { {0.15, 0},    {0.1, 1}     } })
hl.curve("easy",           { type = "spring", mass = 1, stiffness = 238.1191, dampening = 24.21279333 })

-- Animation leafs
hl.animation({ leaf = "global",        enabled = true,  speed = 10,   bezier = "default" })
hl.animation({ leaf = "border",        enabled = true,  speed = 5.39, bezier = "easeOutQuint" })
hl.animation({ leaf = "windows",       enabled = true,  speed = 4.79, spring = "easy" })
hl.animation({ leaf = "windowsIn",     enabled = true,  speed = 4.1,  spring = "easy",         style = "popin 87%" })
hl.animation({ leaf = "windowsOut",    enabled = true,  speed = 1.49, bezier = "linear",       style = "popin 87%" })
hl.animation({ leaf = "fadeIn",        enabled = true,  speed = 1.73, bezier = "almostLinear" })
hl.animation({ leaf = "fadeOut",       enabled = true,  speed = 1.46, bezier = "almostLinear" })
hl.animation({ leaf = "fade",          enabled = true,  speed = 3.03, bezier = "quick" })
hl.animation({ leaf = "workspaces",    enabled = true,  speed = 1.94, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "workspacesIn",  enabled = true,  speed = 1.21, bezier = "almostLinear", style = "fade" })
hl.animation({ leaf = "workspacesOut", enabled = true,  speed = 1.94, bezier = "almostLinear", style = "fade" })

--------------------------------------------------------------------------------
-- 9. LAYOUTS
--------------------------------------------------------------------------------
hl.config({
    dwindle = {
        preserve_split = true,
    },
    master = {
        new_status = "master",
    },
})

--------------------------------------------------------------------------------
-- 10. GESTURES
--------------------------------------------------------------------------------
hl.gesture({
    fingers   = 3,
    direction = "horizontal",
    action    = "workspace",
})

--------------------------------------------------------------------------------
-- 11. MISCELLANEOUS
--------------------------------------------------------------------------------
hl.config({
    misc = {
        enable_swallow           = false,
        force_default_wallpaper = 0,
        disable_hyprland_logo   = true,
    },
})

--------------------------------------------------------------------------------
-- 12. WORKSPACE RULES
--------------------------------------------------------------------------------
-- Example workspace rule definition:
-- hl.workspace_rule({ workspace = "1", monitor = "eDP-1", default = true })

--------------------------------------------------------------------------------
-- 13. WINDOW RULES (WINDOWRULEV2 EQUIVALENTS)
--------------------------------------------------------------------------------
hl.window_rule({
    name   = "gnome-control-center-rule",
    match  = { class = "^(gnome-control-center)$" },
    float  = true,
    size   = { 1050, 720 },
    center = true,
})

--------------------------------------------------------------------------------
-- 14. KEYBINDINGS
--------------------------------------------------------------------------------

-- Session & Compositor exit
hl.bind("CTRL + ALT + Delete", hl.dsp.exit())

-- Applications
hl.bind(mainMod .. " + C",             hl.dsp.exec_cmd("code"))
hl.bind(mainMod .. " + G",             hl.dsp.exec_cmd("steam"))
hl.bind(mainMod .. " + B",             hl.dsp.exec_cmd("brave-origin"))
hl.bind("CTRL + ALT + T",              hl.dsp.exec_cmd(terminal))
hl.bind(mainMod .. " + E",             hl.dsp.exec_cmd("thunar"))
hl.bind(mainMod .. " + I",             hl.dsp.exec_cmd("env XDG_CURRENT_DESKTOP=GNOME gnome-control-center"))
hl.bind(mainMod .. " + SHIFT + Escape",hl.dsp.exec_cmd("ptyxis -e btop"))
hl.bind(mainMod .. " + A",             hl.dsp.exec_cmd("python3 ~/.config/hypr/scripts/drawer.py"))
hl.bind(mainMod .. " + S",             hl.dsp.exec_cmd("python3 ~/.config/hypr/scripts/quicksettings.py"))
hl.bind("CTRL + SHIFT + ALT + B",      hl.dsp.exec_cmd("killall waybar 2>/dev/null; waybar &"))

-- Window management
hl.bind(mainMod .. " + SHIFT + K", hl.dsp.exec_cmd("hyprctl kill"))
hl.bind(mainMod .. " + Q",         hl.dsp.window.close())
hl.bind(mainMod .. " + F11",       hl.dsp.window.float({ action = "toggle" }))
hl.bind("F11",                     hl.dsp.window.fullscreen({ action = "toggle" }))

-- Directional focus (Arrow keys)
hl.bind(mainMod .. " + left",  hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + up",    hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + down",  hl.dsp.focus({ direction = "down" }))

-- Workspaces 1-10: Navigation (SUPER + 0-9) & Move Window (SUPER + SHIFT + 0-9)
for i = 1, 10 do
    local key = i % 10
    hl.bind(mainMod .. " + " .. key,         hl.dsp.focus({ workspace = i }))
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = i }))
end

-- Workspace scrolling with mouse wheel
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }))

-- Mouse drag and resize
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Screenshots (Hyprshot)
local screenshot_dir = "/home/irys/Pictures/Screenshots"
local screenshot_fmt = 'Screenshot from $(date +"%Y-%m-%d %H-%M-%S").png'
hl.bind("Print",                   hl.dsp.exec_cmd(string.format('/home/irys/.local/bin/hyprshot -m output -m active -o "%s" -f "%s"', screenshot_dir, screenshot_fmt)))
hl.bind(mainMod .. " + Print",     hl.dsp.exec_cmd(string.format('/home/irys/.local/bin/hyprshot -m region -o "%s" -f "%s"', screenshot_dir, screenshot_fmt)))
hl.bind(mainMod .. " + SHIFT + S", hl.dsp.exec_cmd(string.format('/home/irys/.local/bin/hyprshot -m window -o "%s" -f "%s"', screenshot_dir, screenshot_fmt)))

-- Hardware & Media Controls (WOB overlay socket integration)
local wob_mute_cmd        = [[pamixer -t && ( [ "$(pamixer --get-mute)" = "true" ] && echo 0 > $XDG_RUNTIME_DIR/wob.sock || pamixer --get-volume > $XDG_RUNTIME_DIR/wob.sock )]]
local wob_vol_down_cmd    = [[pamixer -d 5 && pamixer --get-volume > $XDG_RUNTIME_DIR/wob.sock]]
local wob_vol_up_cmd      = [[pamixer -i 5 && pamixer --get-volume > $XDG_RUNTIME_DIR/wob.sock]]
local wob_bright_down_cmd = [[brightnessctl set 5%- | sed -En 's/.*\(([0-9]+)%\).*/\1/p' > $XDG_RUNTIME_DIR/wob.sock]]
local wob_bright_up_cmd   = [[brightnessctl set 5%+ | sed -En 's/.*\(([0-9]+)%\).*/\1/p' > $XDG_RUNTIME_DIR/wob.sock]]

-- Audio Volume & Mute
hl.bind("XF86AudioMute",        hl.dsp.exec_cmd(wob_mute_cmd),     { locked = true })
hl.bind(mainMod .. " + F1",     hl.dsp.exec_cmd(wob_mute_cmd),     { locked = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd(wob_vol_down_cmd), { locked = true, repeating = true })
hl.bind(mainMod .. " + F2",     hl.dsp.exec_cmd(wob_vol_down_cmd), { locked = true, repeating = true })
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd(wob_vol_up_cmd),   { locked = true, repeating = true })
hl.bind(mainMod .. " + F3",     hl.dsp.exec_cmd(wob_vol_up_cmd),   { locked = true, repeating = true })

-- Display Brightness
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd(wob_bright_down_cmd), { locked = true, repeating = true })
hl.bind(mainMod .. " + F4",       hl.dsp.exec_cmd(wob_bright_down_cmd), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessUp",   hl.dsp.exec_cmd(wob_bright_up_cmd),   { locked = true, repeating = true })
hl.bind(mainMod .. " + F5",       hl.dsp.exec_cmd(wob_bright_up_cmd),   { locked = true, repeating = true })

-- Laptop Input Toggle (Touchpad/Keyboard script)
hl.bind(mainMod .. " + F6", hl.dsp.exec_cmd("~/.config/hypr/scripts/toggle-laptop-inputs.sh"))

-- Display Output Power (DPMS)
hl.bind("XF86Display",      hl.dsp.exec_cmd("hyprctl dispatch dpms toggle"))
hl.bind(mainMod .. " + F8", hl.dsp.exec_cmd("hyprctl dispatch dpms toggle"))

-- Microphone Mute
hl.bind("XF86AudioMicMute", hl.dsp.exec_cmd("pamixer --default-source -t"), { locked = true })
hl.bind(mainMod .. " + F9", hl.dsp.exec_cmd("pamixer --default-source -t"), { locked = true })

