#!/usr/bin/env python3

from subprocess import check_output
from XGetRes import XGetRes

pars = XGetRes()

# Appearance
geometry = pars.xgetres('bar.geometry')
width    = int(check_output("xrandr | grep current | awk '{print $8a}'", shell=True))
font     = pars.xgetres('bar.font')
iconfont = pars.xgetres('bar.iconfont')

bg = pars.xgetres('background')[1:]                         # Do not use it!

back            = "#5F"+bg                                  # Default background "#5F1D1F21"
fore            = pars.xgetres('foreground')                # Default foreground "#FFC5C8C6"
bg_focused      = "#C0"+bg                                  # Bacground for focused workspace
fg_focused      = pars.xgetres('color15')                   # Foreground for focused workspace
bg_inactive     = "#90"+bg                                  # Bacground for inactive workspace
fg_inactive     = pars.xgetres('color7')                    # Foreground for active workspace
bg_urgent       = "#90"+pars.xgetres('color1')[1:]          # Foreground for urgent workspace
bg_sec_1        = "#C0"+bg                                  # Bacground for used section 1
bg_sec_2        = "#A0"+bg                                  # Bacground for used section 2
fg_battery_50   = pars.xgetres('color2')
fg_battery_25   = pars.xgetres('color3')
fg_battery_10   = pars.xgetres('color1')
bg_battery_0    = pars.xgetres('color1')
#color_head      =       # Background for first element "#FFB5BD68"
#color_sec_b1    =       # Background for section 1 "#FF282A2E"
#color_sec_b2    =       # Background for section 2 "#FF454A4F"
#color_sec_b3    =       # Background for section 3 "#FF60676E"
#color_icon      =       # For icons "#FF979997"
#color_mail      =       # Background color for mail alert "#FFCE935F"
#color_chat      =       # Background color for chat alert "#FFCC6666"
#color_cpu       =       # Background color for cpu alert "#FF5F819D"
#color_net       =       # Background color for net alert "#FF5E8D87"
#color_disable   =       # Foreground for disable elements "#FF1D1F21"
#color_wsp       =       # Background for selected workspace "#FF8C9440"

# Device monitoring configuration
#snd_cha=check_output('amixer get Master | grep "Playback channels:" | awk "{if ($4 == '') {printf '%s: Playback', $3} else {printf "%s %s: Playback", $3, $4}}'')

# Monitoring intervals / alerts
#alert_cpu = int(pars.xgetres('bar.alert_cpu'))          # % cpu use
#alert_net = int(pars.xgetres('bar.alert_net'))          # K net use

timer_default = int(pars.xgetres('bar.timer_default'))
timer_vol     = int(pars.xgetres('bar.timer_vol'))       # Volume update
#timer_mail    = int(pars.getres('bar.timer_mail'))    # Mail check update

#default space between sections
stab = '  ' if width > 1024 else ' '

# Char glyps for powerline fonts
sep_left=""                     # Powerline separator left
sep_right=""                    # Powerline separator right
sep_l_left=""                   # Powerline light separator left
sep_l_right=""                  # Powerline light sepatator right

# Icon glyphs from Terminusicons2
icon_clock="Õ"                   # Clock icon
icon_cpu="Ï"                     # CPU icon
icon_mem="Þ"                     # MEM icon
icon_dl="Ð"                      # Download icon
icon_up="Ñ"                      # Upload icon
icon_vol="Ô"                     # Volume icon
icon_hd="À"                      # HD / icon
icon_home="Æ"                    # HD /home icon
icon_mail="Ó"                    # Mail icon
icon_chat="Ò"                    # IRC/Chat icon
icon_music="Î"                   # Music icon
icon_prog="Â"                    # Window icon
icon_contact="Á"                 # Contact icon
icon_wsp="É"                     # Workspace icon

