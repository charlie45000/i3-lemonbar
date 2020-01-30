#!/usr/bin/env python3

from sys import exit, stderr, argv
from os import dup
from Feeder import Feeder
from Bar import Bar
from OptionUsageException import OptionUsageException
from getopt import gnu_getopt, GetoptError
from i3ipc import Connection
from apscheduler.schedulers.background import BackgroundScheduler
from dbus import SystemBus,Interface
from dbus.mainloop import glib as dglib
from gi.repository.GLib import MainLoop
from threading import Thread
from pulsectl import Pulse

bar_pid = 0
socket = None
debug = False
display_title = True


def usage(): #-t mabe not usefull for the moment
    return "Usage: [PATH]/i3_lemonbar.py -b [-s socket] [-a] [-d] [-h]\n"\
           +"   -b,--bar_id=\t\tThe id of the bar in the configuration file\n"\
           +"   -s,--socket=\t\tThe socket of the i3-ipc (optionnal)\n"\
           +"   -a,\t\t\tSets transparency to False (optionnal)\n"\
           +"   -t,\t\t\tIf arguments (thre colorsseparated by commas (hex, no spaces)), set these colors for the title's separator, the background and the foreground (at least the comma must be present. ie: if no colors \",,\" and the defaults will be used. If no arguments, do not display focused title\n"\
           +"   -c,--bar_command\tThe command used for the bar (optionnal, default is /bin/bar)\n"\
           +"   -d,--debug\t\tPrint the feeder string to stdout instead of spawning the bar (optionnal, default is False)\n"\
           +"   -g,--geometry\tset the geometry (refer to bar(1) for more details) (optionnal, default is x14)\n"\
           +"\n/!\\ --bar_id and -t are mandatoty.\n"\
           +"   -h,--help\t\tDispay this help and exits"

def parse_opt():
    try:
        t_color = False
        opts,non_opts = gnu_getopt(argv[1:], 'b:s:c:athd', ['help',
                                                            'bar_id=',
                                                            'socket=',
                                                            'bar_command=',
                                                            'debug'])
        for opt, arg in opts:
            if opt in ['-h', '--help']:
                print(usage())
                exit(0)
            elif opt in ['-b', '--bar_id']:
                bar.id = arg
            elif opt in ['-s', '--socket']:
                global socket
                socket = arg
            elif opt in ['-c', '--bar_command']:
                bar.bar_command = arg
            elif opt in ['-g', '--geometry']:
                bar.geometry = arg
            elif opt == '-a':
                bar.transparency = False
            elif opt == '-t':
                if non_opts:
                    title_colors = non_opts[0].split(',')
                    #bar.colors['ti_sep'] = bar.parse_color(title_colors[0]) if title_colors[0] else '-'
                    bar.colors['ti_bg'] = bar.parse_color(title_colors[1]) if title_colors[1] else '-'
                    bar.colors['ti_fg'] = bar.parse_color(title_colors[2]) if title_colors[2] else '-'
                else:
                    global display_title
                    display_title = False
                t_color = True
            elif opt in ['-d', '--debug']:
                global debug
                debug = True
        if bar.id == '' or not t_color:
            raise OptionUsageException('Error: bar_id and is required if the help argument is not present.')

    except (OptionUsageException, GetoptError) as e:
        print(str(e)+"\n\nWrong arguments usage:\n"+usage(), file=stderr)
        exit(1)


def run():
    loop = MainLoop()
    bus = SystemBus(mainloop=dglib.DBusGMainLoop())
    dglib.threads_init()

    bat_object = bus.get_object('org.freedesktop.UPower', '/org/freedesktop/UPower/devices/battery_BAT1')
    bat = Interface(bat_object, 'org.freedesktop.DBus.Properties')

    lemonbar = Feeder(i3, bat, bus, bar, display_title)
    lemonbar.render_all()

    pulse = Pulse('event-printer')
    pulse.event_mask_set('sink', 'server')
    pulse.event_callback_set(lemonbar.on_volume_event)
    pulse_thread = Thread(target=pulse.event_listen, args=[0])
    pulse_thread.daemon = True
    pulse_thread.start()

    bat_object.connect_to_signal("PropertiesChanged", lemonbar.on_battery_event, dbus_interface='org.freedesktop.DBus.Properties')
    bat_thread = Thread(target=loop.run)
    bat_thread.daemon = True
    bat_thread.start()

    sched = BackgroundScheduler(daemon=True)
    sched.add_job(lemonbar.on_timedate_event, 'cron', second=0)
    sched.start()

    def shutdown(caller, e):
        bar.stop_bar(wbak, bar_pid)
        print(e.change)
        exit(0)

    def reload_bar(caller, data):
        global bar_pid
        bar.stop_bar(wbak, bar_pid)
        #print("reloading...")
        bar_pid = bar.start_bar()
        lemonbar.set_outputs()
        lemonbar.render_all(caller=caller, e=data)

    i3.on('workspace::urgent', lemonbar.on_workspace_event)
    i3.on('workspace::empty', lemonbar.on_workspace_event)
    if display_title:
        i3.on('window::title',    lemonbar.on_window_title_change)
        i3.on('window::close',    lemonbar.on_window_close)
        i3.on('window::focus',    lemonbar.on_window_title_change)
        i3.on('workspace::focus', lemonbar.on_workspace_focus)
    else:
        i3.on('workspace::focus', lemonbar.on_workspace_event)
    i3.on('mode',           lemonbar.on_binding_mode_change)
    i3.on('output',         reload_bar)
    i3.on('shutdown',     shutdown)
    i3.main()

bar = Bar()
parse_opt()
i3 = Connection(socket_path=socket)
bar.set_config(i3)

if not debug:
    wbak = dup(1)
    bar_pid = bar.start_bar()
else: print(bar.bar_args)
run()
