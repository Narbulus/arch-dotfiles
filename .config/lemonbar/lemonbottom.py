#!/usr/bin/python

""" Credit to user 12foo on github """
import i3ipc, lemonpy, threading, os, subprocess, atexit

Widget = lemonpy.Widget
fg = lemonpy.fg
bg = lemonpy.bg
resource = lemonpy.resource
file_contents = lemonpy.file_contents
output_of = lemonpy.output_of

i3 = i3ipc.Connection()
i3_main_thread = threading.Thread(target=i3.main)

class Workspaces(Widget):
    def __init__(self, pipe, hooks):
        self.focused = '1'
        def update_focus(self, e):
            msg = 'Workspace changed:' + e.current.name + '\n'
            os.write(pipe, msg.encode('utf-8'))
        i3.on('workspace::focus', update_focus)
        hooks['Workspace changed'] = self
    def update(self, line):
        if (line):
            self.focused = line.split(':')[1]
    def render(self):
        result = ''
        icon = "\ue1bc"
        i3tree = i3.get_tree()
        workspaces = {}
        color = 'color_text'
        for workspace in i3tree.workspaces():
            workspaces[workspace.name] = workspace
        for i in range(1, 11):
            if str(i) in workspaces:
                icon = "\ue1c2"
            else:
                icon = "\ue1bc"
            if str(i) == self.focused:
                color = 'color_text'
            else:
                color = 'color_fade'
            result += ' ' + fg(color, icon)
        return result

class WindowName(Widget):
    def __init__(self, pipe, hooks):
        self.window = ''
        def update_window(self, e):
            msg = 'Window changed\n'
            os.write(pipe, msg.encode('utf-8'))
        i3.on('window::focus', update_window)
        hooks['Window changed'] = self
    def update(self, line):
        if (line):
            focused = i3.get_tree().find_focused()
            if (focused):
                if (hasattr(focused, 'window_class') and focused.window_class):
                    windowname = focused.window_class
                elif (hasattr(focused, 'title') and focused.title):
                    windowname = focused.title
                else:
                    windowname = 'Unknown window'
                self.window = str(focused.workspace().num) + ' : ' + windowname
    def render(self):
        return fg('color_fore', '[' + self.window + ']')

print('after')
class CPU(Widget):
    def __init__(self, pipe, hooks):
        self.conkystate = ''
        client = subprocess.Popen(['conky -c ~/.config/lemonbar/conky_config'], stdout=pipe, shell=True)
        hooks['Conky Output:'] = self
    def update(self, line):
        if (line):
            self.conkystate = line.split(':')[1]
    def render(self):
        return self.conkystate.replace('color_fore', resource('color_fore')) + ' ' 

sep = fg('color_fade', ' | ')

widgets = ['%{l} ', WindowName, '%{c}', Workspaces, '%{r}', CPU]

# Start listening for i3 events after creating widgets
lemonpy.runwidgets(widgets, i3_main_thread.start)
