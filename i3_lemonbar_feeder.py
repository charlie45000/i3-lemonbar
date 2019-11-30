#!/usr/bin/env python3

import os
import sys
import time
import i3ipc
from apscheduler.schedulers.background import BackgroundScheduler
import dbus
import dbus.mainloop.glib
from gi.repository import GLib as glib
from signal import SIGTERM
from threading import Thread
from subprocess import check_output
from pulsectl import Pulse
from i3_lemonbar_conf import *

running = True

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


class LemonBar(object):

    def __init__(self, i3, bat, bus):
        self.out                = ''
        self.datetime           = ''
        self.workspaces         = dict()
        self.title              = ' %%{R B-}%s%%{F-}'  % sep_right

        self.volume             = ''
        self.battery            = ''
        self.i3                 = i3
        self.focusedWinTitle    = self.i3.get_tree().find_focused().name
        self.currentBindingMode = ''
        self.mode               = ''
        self.bat                = bat
        self.bus                = bus
        self.pulse              = Pulse('my-client-name')
        self.outputs            = self.get_outputs()

    def get_outputs(self):
        mon = [[out.name, out.rect.x, out.rect.y] for out in self.i3.get_outputs() if out.active]
        quickSort(mon, 0, len(mon)-1)
        return [el[0] for el in mon]

    def on_battery_event(self, device, props, signature):
        perc = round(self.bat.Get(device, "Percentage"))
        state = self.bat.Get(device, "State")
        timeleft = self.bat.Get(device, "TimeToEmpty" if state==2 else "TimeToFull")
        self.render_battery(perc, state, timeleft)
        for idx, output in enumerate(self.outputs):
            self.display(idx)
        print('')
        sys.stdout.flush()

    def on_binding_mode_change(self, caller, e):
        self.currentBindingMode = e.change
        if self.currentBindingMode != "default":
            self.render_binding_mode()
        else:
            self.mode = ''
        
        for idx, output in enumerate(self.outputs):
            self.display(idx)
        print('')
        sys.stdout.flush()

    def on_workspace_focus(self, caller, e):
        self.title=" %%{R B-}%s%%{F-}" % sep_right
        for idx,output in enumerate(self.outputs):
            self.render_workspaces(index=idx, display=output)
            self.display(idx)        
        print('')
        sys.stdout.flush()

    def on_timedate_event(self):
        self.render_datetime()

        for idx, output in enumerate(self.outputs):
            self.display(idx)
        print('')
        sys.stdout.flush()

    def on_window_title_change(self, caller, e):
        self.focusedWinTitle = e.container.name
        self.render_focused_title()
        fd=open('/tmp/lemonbar', 'a')
        try:
            for idx, output in enumerate(self.outputs):
                self.display(idx)
            print('')
            sys.stdout.flush()
        except:
            fd.write('error title change\n')
        fd.write('yes!!\n')

    def on_volume_event(self, ev):
        default_output_sink_name = self.pulse.server_info().default_sink_name
        sink = self.pulse.get_sink_by_name(default_output_sink_name)
        self.render_volume(sink)
        
        for idx, output in enumerate(self.outputs):
            self.display(idx)
        print('')
        sys.stdout.flush()


    def render_workspaces(self, index, display):
        wsp_icon = "%%{F- B%s} %%{T2}%s%%{T1}" % (bg_inactive,
                                                 icon_wsp)
        wsp_items = ''

        for wsp in self.i3.get_workspaces():
            wsp_name = wsp.name
            wsp_action = "%%{A:i3-msg workspace %s}" % wsp_name
            if wsp.output != display :#and not wsp.urgent:
                continue
            if wsp.focused:
                wsp_items += " %%{R B%s}%s%s%%{F%s T1} %s%%{A}" % (bg_focused,
                                                                sep_right,
                                                                wsp_action,
                                                                fg_focused,
                                                                wsp_name)
            elif wsp.urgent:
                wsp_items += " %%{R B%s}%s%s%%{F- T1} %s%%{A}" % (bg_urgent,
                                                                sep_right,
                                                                wsp_action,
                                                                wsp_name)	
            else:
                if not wsp_items:
                    wsp_items += "  %s%%{T1} %s%%{A}" % (wsp_action,
                                                        wsp_name)
                else:
                    wsp_items += " %%{R B%s}%s%s%%{F- T1} %s%%{A}" % (bg_inactive,
                                                                    sep_right,
                                                                    wsp_action,
                                                                    wsp_name)

        self.workspaces[index] = '%s%s' % (wsp_icon, wsp_items)

    def render_focused_title(self):
        self.title = " %%{R B%s}%s%%{F%s T2} %s %%{T1}%s %%{R B-}%s%%{F-}" % (bg_sec_1,
                                                                            sep_right,
                                                                            fore,
                                                                            icon_prog,
                                                                            self.focusedWinTitle,
                                                                            sep_right)

    def render_binding_mode(self):
        self.mode = " %%{R B%s}%s%%{F%s} %%{T1} %s" % (bg_sec_2,
                                                        sep_right,
                                                        fg_battery_10,
                                                        self.currentBindingMode)

    def render_datetime(self):
        cdate = " %%{F%s}%s%%{R F%s} %%{T2}%s%%{T1} %s" % (bg_sec_2,
                                                        sep_left,
                                                        fore,
                                                        icon_clock,
                                                        time.strftime("%d-%m-%Y"))
        ctime = " %%{F%s}%s%%{R F%s} %s %%{F- B-}" % (bg_sec_1,
                                                    sep_left,
                                                    fore,
                                                    time.strftime("%H:%M"))
        self.datetime = "%s%s" % (cdate, ctime)

    def render_volume(self, sink):
        value = round(sink.volume.value_flat*100)
        mute = bool(sink.mute)
        volume = str(value)+'%%' if not mute else 'MUTE'
        self.volume = "%%{F%s}%s%%{R F%s} %%{T2}%s%%{T1} %s" %(bg_sec_2,
                                            sep_left,
                                            fore,
                                            icon_vol,
                                            volume)

    def render_battery(self, val, state, timeleft):
        value =  str(val) + "%%"
        remaining = " (%s)" % time.strftime("%H:%M", time.gmtime(timeleft)) if timeleft>0 else ''
        fg = fore
        bg = bg_sec_1
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
                                                    sep_left,
                                                    fg,
                                                    value,
                                                    remaining)

    def render_all(self, caller=None, e=None):
    # Render one bar per each output
        #self.render_focused_title()
        device = "org.freedesktop.UPower.Device"
        perc = round(self.bat.Get(device, "Percentage"))
        state = self.bat.Get(device, "State")
        timeleft = self.bat.Get(device, "TimeToEmpty" if state==2 else "TimeToFull")
        default_output_sink_name = self.pulse.server_info().default_sink_name
        sink = self.pulse.get_sink_by_name(default_output_sink_name)

        self.render_battery(perc, state, timeleft)
        self.render_datetime()
        self.render_battery(perc, state, timeleft)
        self.render_volume(sink)

        for idx,output in enumerate(self.outputs):
            self.render_workspaces(index=idx, display=output)
            self.display(idx)

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


def refresh(bat_object, interface):
    refresh_method = bat_object.get_dbus_method('Refresh', interface)
    timeout = 30
    while running:
        try:
            refresh_method()
            time.sleep(timeout)
            #print(running, file=sys.stderr)
            #sys.stderr.flush()
        except:
            print('error refresh', file=sys.stderr)
            sys.stderr.flush()
            return

def shutdown(caller, test=None):
    print(test)
    running = False
    lemonpid = int(check_output('pidof -s bar', shell=True))

    if lemonpid:
        os.kill(lemonpid, SIGTERM)
    sys.exit(0)
    
def run():
    i3 = i3ipc.Connection()
    #i3.auto_reconnect = True
    #i3thread = Thread(target=i3.main)
    #i3thread.daemon = True

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    bat_object = bus.get_object('org.freedesktop.UPower', '/org/freedesktop/UPower/devices/battery_BAT1')
    bat = dbus.Interface(bat_object, 'org.freedesktop.DBus.Properties')
        
    lemonbar = LemonBar(i3, bat, bus)
    lemonbar.render_all()

    pulse = Pulse('event-printer')
    pulse.event_mask_set('sink', 'server')
    pulse.event_callback_set(lemonbar.on_volume_event)
    pulse_thread = Thread(target=pulse.event_listen, args=[0])
    pulse_thread.daemon = True
    pulse_thread.start()

    bat_object.connect_to_signal("PropertiesChanged", lemonbar.on_battery_event, dbus_interface='org.freedesktop.DBus.Properties')
    loop = glib.MainLoop()
    bat_thread = Thread(target=loop.run)
    bat_thread.daemon = True
    bat_thread.start()

    refresh_thread = Thread(target=refresh, args=(bat_object, 'org.freedesktop.UPower.Device'))
    refresh_thread.daemon = True
    refresh_thread.start()

    sched = BackgroundScheduler(daemon=True)
    sched.add_job(lemonbar.on_timedate_event, 'cron', second=0)
    sched.start()

    i3.on('workspace::focus', lemonbar.on_workspace_focus)
    i3.on('window::title',    lemonbar.on_window_title_change)
    i3.on('window::focus',    lemonbar.on_window_title_change)
    i3.on('window::urgent',   lemonbar.on_workspace_focus)
    i3.on('mode::',           lemonbar.on_binding_mode_change)
    i3.on('ipc-shutdown',     shutdown)
    i3.on('barconfig_update', shutdown)
    #i3thread.start()
    i3.main()
    
   # input()
    #refresh(bat_object, 'org.freedesktop.UPower.Device')
