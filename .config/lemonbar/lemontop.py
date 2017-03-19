#!/usr/bin/python

""" Credit to user 12foo on github """
import os, sys, select, datetime, subprocess, atexit, lemonpy

Widget = lemonpy.Widget
fg = lemonpy.fg
bg = lemonpy.bg
resource = lemonpy.resource
file_contents = lemonpy.file_contents
output_of = lemonpy.output_of

# Countdown to Lola
lola_date = datetime.date(2017, 3, 17)

class Clock(Widget):
    def render(self):
        date=fg('color_fore', datetime.datetime.now().strftime('[%a %b %d]'))
        time=fg('color_text', datetime.datetime.now().strftime('%H:%M'))
        return date + ' ' + time

class Battery(Widget):
    def available():
        return file_contents('/sys/class/power_supply/BAT0/present') == '1'
    def render(self):
        try:
            charge = int(file_contents('/sys/class/power_supply/BAT0/capacity'))
        except:
            charge = 0
        c = resource('color_alert') if charge < 30 else resource('color_text')
        if file_contents('/sys/class/power_supply/BAT0/status') != 'Discharging':
            status = fg('color_high', '[chg]')
        else:
            status = fg('color_fore', '[bat]')
        return status + ' ' + str(charge) + '%'

class Network(Widget):
    def render(self):
        status = ''
        netstatus = output_of(['iwgetid']).split()
        if len(netstatus) == 0:
            return fg('color_fade', '[net] disconnected')
        elif len(netstatus) < 2 or 'ESSID' not in netstatus[1]:
            return fg('color_high', '[net] connecting')
        else:
            status = netstatus[1][7:-1]
            if status == '':
                return fg('color_fade', '[net] disconnected')
        return fg('color_fore', '[net] ') + status

class PulseAudio(Widget):
    @staticmethod
    def available():
        try:
            subprocess.run(['pactl', 'info'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except:
            return False
    def __init__(self, pipe, hooks):
        client = subprocess.Popen(['pactl', 'subscribe'], stdout=pipe)
        atexit.register(client.kill)
        self.volume = 0
        self.mute = False
        hooks["Event 'change' on sink"] = self
    def update(self, line):
        painfo = output_of(['pactl', 'info']).splitlines()
        look_for = None
        for l in painfo:
            if l.startswith('Default Sink:'):
                look_for = l.split(':')[1].strip()
                break
        in_sink = False
        look_for = 'Name: ' + look_for
        sink_list = output_of(['pactl', 'list', 'sinks']).splitlines()
        for l in sink_list:
            if not in_sink:
                if look_for in l:
                    in_sink = True
            else:
                if 'Mute:' in l:
                    if l.split(':')[1].strip() == 'yes':
                        self.mute = True
                    else:
                        self.mute = False
                elif 'Volume:' in l:
                    self.volume = int(l.split('/', 2)[1].strip()[:-1])
                    return
    def render(self):
        if self.mute:
            return fg('color_alert', '[mute] ') + fg('color_text', str(self.volume))
        else:
            return fg('color_fore', '[vol] ') + fg('color_text', str(self.volume))

class CountdownToLola(Widget):
    def render(self):
        date_diff = lola_date - datetime.date.today()
        tag = fg('color_fore', "[days to lola]") 
        days = fg('color_text', str(date_diff.days))
        heart = fg('color_fade', ' \ue106')
        return tag + heart + days + heart

sep = fg('color_fade', ' | ')

widgets = ['%{l} ', Clock, '%{c}', CountdownToLola, '%{r}', PulseAudio, sep, Network, sep, Battery, ' ']

lemonpy.runwidgets(widgets)
