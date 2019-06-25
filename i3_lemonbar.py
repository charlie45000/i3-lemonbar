#!/usr/bin/env python3

import os
from i3_lemonbar_conf import *
from subprocess import call


cwd = os.path.dirname(os.path.abspath(__file__))
lemon = "bar -p -f '%s' -f '%s' -g '%s' -B '%s' -F '%s' -a 10" % (font, iconfont,  geometry, back, fore)
print(geometry, width)
feed = "python3 -c 'import i3_lemonbar_feeder; i3_lemonbar_feeder.run()'"
print('cd %s; %s | %s' % (cwd, feed, lemon))

call('cd %s; %s | %s' % (cwd, feed, lemon), shell=True)
