#!/usr/bin/bash

laptop="eDP1"
external="HDMI1"

if (xrandr | grep -e "^$external connected"); then
    echo "hey"
    xrandr --output $laptop --primary --mode 1920x1080 --rotate normal
    xrandr --output $external --above $laptop --mode 1920x1080 --rotate normal
    DISPLAY=:0.1; feh --bg-scale ~/Media/mononoke.png
fi
DISPLAY=:0.0; feh --bg-scale ~/Media/mononoke.png
