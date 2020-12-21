#!/bin/sh

userresources=$HOME/.Xresources
usermodmap=$HOME/.Xmodmap
sysresources=/etc/X11/xinit/.Xresources
sysmodmap=/etc/X11/xinit/.Xmodmap
gensettings=$HOME/.urxvt/Xresources
colorsettings=$HOME/.urxvt/colors/dark

# merge in defaults and keymaps
if [ -f $sysresources ]; then
   xrdb -merge $sysresources
fi
if [ -f $sysmodmap ]; then
    xmodmap $sysmodmap
fi
if [ -f "$userresources" ]; then
    xrdb -merge "$userresources"
fi
if [ -f "$usermodmap" ]; then
    xmodmap "$usermodmap"
fi
if [ -f "$gensettings" ]; then
    xrdb -merge "$gensettings"
fi
if [ -f "$colorsettings" ]; then
    xrdb -merge "$colorsettings"
fi

# start some nice programs
if [ -d /etc/X11/xinit/xinitrc.d ] ; then
 for f in /etc/X11/xinit/xinitrc.d/?*.sh ; do
  [ -x "$f" ] && . "$f"
 done
 unset f
fi

# urxvt daemon for performance
urxvtd -q -f -o
echo $HOME > $HOME/.urxvt/cwd

# NVIDIA settings
#xrandr --setprovideroutputsource modesetting NVIDIA-0
#xrandr --auto
# dual monitor command
xrandr --output HDMI-1-2 --auto --right-of eDP-1-1
#xrandr --output HDMI-1-2 --auto --above eDP-1-1

numlockx & #number lock
xset r rate 250 30 #key rates for key delay and repeat

# postgresql
sudo systemctl start postgresql

~/.wallpaper/.fehbg &
unclutter -idle 3&
touchpad_toggle
statusbar
exec /home/bk/pkg/dwm/dwm
