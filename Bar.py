from os import pipe, fork, close, dup2, kill, environ, execve
from sys import exit
from re import compile as comp
from signal import SIGTERM

class Bar(object):
    def __init__(self):
        self.id = ''
        self.transparency = True
        #self.bar_command = '/bin/bar'
        self.bar_command = '/bin/lemonbar'
        self.bar_args = ['-g']
        #self.config = dict()
        self.colors = dict()
        self.sep_right = ' | '
        self.sep_left = ' | '
        self.geometry = 'x14'

    def start_bar(self):
        brside, bwside = pipe()
        srside, swside = pipe()

        bar_pid = fork()
        if not bar_pid:
            close(bwside)
            close(srside)

            dup2(brside, 0)
            dup2(swside, 1)

            execve(self.bar_command, [self.bar_command] + self.bar_args + ['|', 'sh'], environ)
            print("failed to exec program!", file=sys.stderr)
            exit(1)
        close(brside)
        close(swside)
        sh_pid = fork()
        if not sh_pid:
            close(bwside)
            dup2(srside, 0)
            execve('/bin/sh', ['/bin/sh'], environ)
            print("failed to exec program!", file=sys.stderr)
            exit(1)
        close(srside)
        dup2(bwside, 1)
        return bar_pid, sh_pid #TODO: do not kill sh if possible

    def stop_bar(self, wbak, bar_pid, sh_pid):
            dup2(wbak, 1)

            if bar_pid:
                kill(bar_pid, SIGTERM)
            else: print("could'nt stop bar")
            if sh_pid:
                kill(sh_pid, SIGTERM) #TODO: change that!
            else: print("could'nt stop shell")

    def parse_color(self, color):
        hex_color = "[A-Fa-f0-9]"
        norm_color = comp("^#"+hex_color+"{6}$")
        trans_color_1 = comp("^\[("+hex_color+"{2})\]#("+hex_color+"{6})$")
        trans_color_2 = comp("^#"+hex_color+"{2}("+hex_color+"{6})$")
        if (match:=trans_color_1.match(color)):
            return '#'+match.group(1)+match.group(2) if self.transparency else '#'+match.group(2)
        elif (match:=trans_color_2.match(color)):
            return color if self.transparency else '#'+match.group(1)
        elif norm_color.match(color):
            return color
        return '#f0f0f0'

    def set_config(self, i3):
        #status_command, stiped numbers and name, mode, tray padding, modifier, verbose, workspace buttons and hidden state are ignored. TODO: implement them.
        config = i3.get_bar_config(self.id)

        self.bar_args += [self.geometry]
        if config.font:
            for font in config.font.split(','):
                self.bar_args += ['-f'] + [font]
        if config.colors['background']:
            self.colors['gen_bg'] = config.colors['background'][-6:]
            self.bar_args += ['-B'] + [self.parse_color(config.colors['background'])]
        if config.colors['statusline']:

            self.bar_args += ['-F'] + [self.parse_color(config.colors['statusline'])]
        if not config.position == 'top':
            self.bar_args += ['-b']
        if config.separator_symbol:
            separators = config.separator_symbol.split(',')
            self.sep_left = separators[0]
            if len(separators) == 2:
                self.sep_right = separators[1]
            else:
                self.sep_right = separators[0]
        for key, value in config.colors.items():
            if key in ['statusline', 'background']:
                continue
#            elif key == 'focused_workspace_border':
#                self.colors['foc_sep'] = self.parse_color(value)
            elif key == 'focused_workspace_bg':
                self.colors['foc_bg'] = self.parse_color(value)
            elif key == 'focused_workspace_text':
                self.colors['foc_fg'] = self.parse_color(value)
#            elif key == 'inactive_workspace_border':
#                self.colors['in_sep'] = self.parse_color(value)
            elif key == 'inactive_workspace_bg':
                self.colors['in_bg'] = self.parse_color(value)
            elif key == 'inactive_workspace_text':
                self.colors['in_fg'] = self.parse_color(value)
#            elif key == 'urgent_workspace_border':
#                self.colors['ur_sep'] = self.parse_color(value)
            elif key == 'urgent_workspace_bg':
                self.colors['ur_bg'] = self.parse_color(value)
            elif key == 'urgent_workspace_text':
                self.colors['ur_fg'] = self.parse_color(value)
#            elif key == 'binding_mode_border':
#                self.colors['bd_sep'] = self.parse_color(value)
            elif key == 'binding_mode_bg':
                self.colors['bd_bg'] = self.parse_color(value)
            elif key == 'binding_mode_text':
                self.colors['bd_fg'] = self.parse_color(value)
