# i3-lemonbar

Status script and configuration for [Lemonbar](https://github.com/LemonBoy/bar) and [i3wm](https://i3wm.org/).

Configuration is taken from beautiful powerline setup by [electro7](https://github.com/electro7/dotfiles/tree/master/.i3/lemonbar).

Status feeder script is written completely in Python and uses [i3ipc](https://github.com/acrisci/i3ipc-python) for most of the interaction with i3.

### Features

* Event-based, rather than periodically updated
* Multiple display output support

### Installation

* Install [lemonbar](https://github.com/LemonBoy/bar).
* Install [i3ipc-python](https://github.com/acrisci/i3ipc-python) library.
```
        pip install i3ipc
```
* Make sure you have terminus and terminesspowerline fonts installed. You can get them [here](https://github.com/electro7/dotfiles).
* Clone this repo (e.g. to your .i3 directory).
```
        mkdir ~/.i3/lemonbar && git clone https://github.com/mirekys/i3-lemonbar.git ~/.i3/lemonbar
```
* Configure i3 to use Lemonbar. (this is just an exemple, all the color variables are hier "#rrggbb". you can use multiple color formating: [aa]#rrggbb (aa in hex), #rrggbb, #aarrggbb.

```
        bar {
#       default general config
	id bar-0
	position top
	workspace_buttons yes
	strip_workspace_numbers no
	strip_workspace_name no
	binding_mode_indicator yes
	modifier $mod

#	commands
	i3bar_command "$I3C/lemonbar/i3_lemonbar.py -t ,[c0]#000000,"

#	font (the first is used for the text and the other for the icons)
	set_from_resource $genfont bar.font	-xos4-terminesspowerline-medium-r-normal--12-120-72-72-c-60-iso10646-1
	set_from_resource $icofont bar.iconfont	-xos4-terminusicons2mono-medium-r-normal--12-120-72-72-m-60-iso8859-1
	font "$genfont,$icofont"

#	separators used by the bar.separated by commas
#	#powerline separators (warnig: make sure that the end of each line is empty):
		set $sep_right 
		set $sep_left 
	separator_symbol "$sep_left,$sep_right"

	colors {
 	background	"[5F]$xbg"
	statusline	$xfg

#	class name		border		background	text
	focused_workspace	"[C0]$xbg"	"[C0]$xbg"	$xfg
	inactive_workspace	"[90]$xbg"	"[90]$xbg"	$c07
	urgent_workspace	"[90]$c01"	"[90]$c01"	$c07
	binding_mode		"[A0]$xbg"	"[A0]$xbg"	$c01
	}
}
```
