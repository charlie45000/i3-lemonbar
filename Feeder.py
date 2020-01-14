#!/usr/bin/env python3

from sys import stderr
from time import strftime, gmtime
from i3_lemonbar_conf import fg_battery_50, fg_battery_25, fg_battery_10, bg_battery_0, icon_clock, icon_vol, icon_wsp, icon_prog
from pulsectl import Pulse

def sort_cb(el1, el2):
    if el1[1] < el2[1] or el1[2] < el2[2]:
        return -1
    elif el1[1] > el2[1] or el1[2] > el2[2]:
        return 1
    else:
        return 0

def partition(arr, low, high):
    i = ( low-1 )         # index of smaller element
    pivot = arr[high]     # pivot

    for j in range(low , high):
        # If current element is smaller than or
        # equal to pivot
        if   sort_cb(arr[j], pivot) <= 0:
            # increment index of smaller element
            i = i+1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i+1], arr[high] = arr[high], arr[i+1]
    return ( i+1 )

# The main function that implements QuickSort
# arr[] --> Array to be sorted,
# low  --> Starting index,
# high  --> Ending index

# Function to do Quick sort
def quickSort(arr, low, high):
    if low < high:
        # pi is partitioning index, arr[p] is now
        # at right place
        pi = partition(arr, low, high)

        # Separately sort elements before
        # partition and after partition
        quickSort(arr, low, pi-1)
        quickSort(arr, pi+1, high)


class Feeder(object):

    def __init__(self, i3, bat, bus, bar, display_title=True):
        self.out                = ''
        self.datetime           = ''
        self.workspaces         = dict()
        self.volume             = ''
        self.battery            = ''
        self.i3                 = i3
        self.bar                = bar
        self.display_title      = display_title
        focused = i3.get_tree().find_focused()
        self.focusedWinTitle    = focused.name if not focused.type=='workspace' and  display_title else ''
        self.currentBindingMode = ''
        self.mode               = ''
        self.bat                = bat
        self.bus                = bus
        self.pulse              = Pulse('my-client-name')
        self.outputs            = ''
        self.notitle            = " %%{R B-}%s%%{F-}" % self.bar.sep_left
        self.title              = self.notitle

        self.set_outputs()

    def set_outputs(self):
        mon = [[out.name, out.rect.x, out.rect.y] for out in self.i3.get_outputs() if out.active]
        quickSort(mon, 0, len(mon)-1)
        self.outputs =  [el[0] for el in mon]

    def on_battery_event(self, device, props, signature):
        perc = round(self.bat.Get(device, "Percentage"))
        state = self.bat.Get(device, "State")
        timeleft = self.bat.Get(device, "TimeToEmpty" if state==2 else "TimeToFull")
        self.render_battery(perc, state, timeleft)
        for idx, output in enumerate(self.outputs):
            self.display(idx)
        print('')
        #print('bat', file=stderr)

    def on_binding_mode_change(self, caller, e):
        self.currentBindingMode = e.change
        if self.currentBindingMode != "default":
            self.render_binding_mode()
        else:
            self.mode = ''

        for idx, output in enumerate(self.outputs):
            self.display(idx)
        print('')
        #print('bind', file=stderr)

    def on_workspace_focus(self, caller, e):
        self.focusedWinTitle = e.current.find_focused()
        if not self.focusedWinTitle:
           self.title = self.notitle

        self.on_workspace_event(caller, e)
        #print('wksp2', file=stderr)

    def on_workspace_event(self, caller, e):
        for idx,output in enumerate(self.outputs):
            self.render_workspaces(index=idx, display=output)
            self.display(idx)
        print('')
        #print('wksp1', file=stderr)

    def on_timedate_event(self):
        self.render_datetime()

        for idx, output in enumerate(self.outputs):
            self.display(idx)
        print('')
        #print('time', file=stderr)

    def on_window_close(self, caller, e):
        focusedWin = self.i3.get_tree().find_focused()
        if not focusedWin.type=='workspace':
            self.focusedWinTitle = focusedWin.name
            self.render_focused_title()
            try:
                for idx, output in enumerate(self.outputs):
                    self.display(idx)
                print('')
            except:
                fd=open('/tmp/lemonbar', 'a')
                fd.write('error title change\n')
        else:
            self.title = self.notitle
            for idx, output in enumerate(self.outputs):
                    self.display(idx)
            print('')


    def on_window_title_change(self, caller, e):
        self.focusedWinTitle = e.container.name
        self.render_focused_title()
        try:
            for idx, output in enumerate(self.outputs):
                self.display(idx)
            print('')
        except:
            fd=open('/tmp/lemonbar', 'a')
            fd.write('error title change\n')

    def on_volume_event(self, ev):
        default_output_sink_name = self.pulse.server_info().default_sink_name
        sink = self.pulse.get_sink_by_name(default_output_sink_name)
        self.render_volume(sink)

        for idx, output in enumerate(self.outputs):
            self.display(idx)
        print('')
        #print('vol', file=stderr)

    def render_workspaces(self, index, display):
        wsp_icon = "%%{F- B%s} %%{T2}%s%%{T1}" % (self.bar.colors['in_bg'],
                                                 icon_wsp)
        wsp_items = ''
        sep = self.bar.sep_left

        for wsp in self.i3.get_workspaces():
            wsp_name = wsp.name
            wsp_action = "%%{A1:i3-msg -q workspace %s:}" % wsp_name
            if wsp.output != display :#and not wsp.urgent:
                continue
            if wsp.focused:
                wsp_items += " %%{R B%s}%s%s%%{F%s T1} %s%%{A}" % (self.bar.colors['foc_bg'],
                                                                sep,
                                                                wsp_action,
                                                                self.bar.colors['foc_fg'],
                                                                wsp_name)
            elif wsp.urgent:
                wsp_items += " %%{R B%s}%s%s%%{F- T1} %s" % (self.bar.colors['ur_bg'],
                                                                sep,
                                                                wsp_action,
                                                                wsp_name)
            else:
                if not wsp_items:
                    wsp_items += "  %s%%{T1} %s%%{A}" % (wsp_action,
                                                        wsp_name)
                else:
                    wsp_items += " %%{R B%s}%s%s%%{F- T1} %s%%{A}" % (self.bar.colors['in_bg'],
                                                                    sep,
                                                                    wsp_action,
                                                                    wsp_name)

        self.workspaces[index] = '%s%s' % (wsp_icon, wsp_items)

    def render_focused_title(self):
        sep = self.bar.sep_left
        self.title = " %%{R B%s}%s%%{F- T2} %s %%{T1}%s %%{R B-}%s%%{F-}" % (self.bar.colors['ti_bg'],
                                                                            sep,
                                                                            icon_prog,
                                                                            self.focusedWinTitle,
                                                                            sep)

    def render_binding_mode(self):
        self.mode = " %%{R B%s}%s%%{F%s} %%{T1} %s" % (self.bar.colors['bd_bg'],
                                                        self.bar.sep_left,
                                                        self.bar.colors['bd_fg'],
                                                        self.currentBindingMode)

    def render_datetime(self):
        sep = self.bar.sep_right
        cdate = " %%{F%s}%s%%{R F-} %%{T2}%s%%{T1} %s" % ('#A0'+self.bar.colors['gen_bg'],
                                                        sep,
                                                        icon_clock,
                                                        strftime("%d-%m-%Y"))
        ctime = " %%{F%s}%s%%{R F-} %s %%{B-}" % (self.bar.colors['foc_bg'],
                                                    sep,
                                                    strftime("%H:%M"))
        self.datetime = "%s%s" % (cdate, ctime)

    def render_volume(self, sink):
        value = round(sink.volume.value_flat*100)
        mute = bool(sink.mute)
        volume = str(value)+'%' if not mute else 'MUTE'
        self.volume = "%%{F%s}%s%%{R F-} %%{T2}%s%%{T1} %s" %('#A0'+self.bar.colors['gen_bg'],
                                                            self.bar.sep_right,
                                                            icon_vol,
                                                            volume)

    def render_battery(self, val, state, timeleft):
        value =  str(val) + "%"
        remaining = " (%s)" % strftime("%H:%M", gmtime(timeleft)) if timeleft>0 else ''
        fg = '-'
        bg = self.bar.colors['foc_bg']
        if state == 2:
            if val > 50:
                fg = fg_battery_50
            elif val > 25:
                fg = fg_battery_25
            elif val > 10:
                fg = fg_battery_10
            else:
                bg = bg_battery_0
        self.battery = " %%{F%s}%s%%{R F%s} %s%s" % (bg,
                                                    self.bar.sep_right,
                                                    fg,
                                                    value,
                                                    remaining)

    def render_all(self, caller=None, e=None):
    # Render one bar per each output
        if e == None:
            device = "org.freedesktop.UPower.Device"
            perc = round(self.bat.Get(device, "Percentage"))
            state = self.bat.Get(device, "State")
            timeleft = self.bat.Get(device, "TimeToEmpty" if state==2 else "TimeToFull")
            default_output_sink_name = self.pulse.server_info().default_sink_name
            sink = self.pulse.get_sink_by_name(default_output_sink_name)

            self.render_battery(perc, state, timeleft)
            self.render_datetime()
            self.render_volume(sink)
            if not self.focusedWinTitle == '': self.render_focused_title()

        for idx,output in enumerate(self.outputs):
            self.render_workspaces(index=idx, display=output)
            self.display(idx)
        print('')

    def display(self, idx):
        #self.render_volume(0)
        self.out = "%%{S%d}%%{l}%s%s%s%%{r}%s%s%s" % (idx,
                                                    self.workspaces[idx],
                                                    self.mode,
                                                    self.title,
                                                    self.volume,
                                                    self.battery,
                                                    self.datetime)
        print(self.out, end='')
