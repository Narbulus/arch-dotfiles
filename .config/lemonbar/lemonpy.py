#!/usr/bin/python

""" Credit to user 12foo on github """
import os, sys, select, datetime, subprocess, atexit

# All resources are prefixed to avoid environment
# variable naming collisions
resource_prefix = "LEM_RES_"

# Tries to load a color from the environment
# this should have been loaded from lemconfig
def resource(name):
    try:
        return os.environ[resource_prefix + name]
    except:
        print("INVALID RESOURCE: " + name)
        return ""

def fg(color, text):
    return '%{F' + resource(color) + '}' + text + '%{F-}'

def bg(color, text):
    return '%{B' + resource(color) + '}' + text + '%{B-}'
    

# Attempts to read the contents of a file
def file_contents(f):
    try:
        ff = open(f, 'r')
        c = ff.read().strip()
        ff.close()
        return c
    except:
        return None

def output_of(cmd):
    try:
        return subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
    except:
        return None

class Widget(object):
    @staticmethod
    def available():
        return True
    def __init__(self, pipe, hooks):
        pass
    def update(self, line):
        pass
    def render(self):
        return ''

class Text(Widget):
    def __init__(self, text):
        super(Widget, self)
        self.text = text
    def render(self):
        return self.text

def runwidgets(widgets, postinit=None):
    if __name__ == 'lemonpy':
        sread, swrite = os.pipe()
        hooks = {}

        ws = []
        for wc in widgets:
            if type(wc) is str:
                w = Text(wc)
                ws.append(w)
            elif wc.available():
                w = wc(swrite, hooks)
                w.update(None)
                ws.append(w)

        if (postinit):
            postinit()

        print(''.join(w.render() for w in ws))
        sys.stdout.flush()

        while True:
            ready, _, _ = select.select([sread], [], [], 5)
            updated = False
            if len(ready) > 0:
                for p in ready:
                    lines = os.read(p, 4096).decode('utf-8').splitlines()
                    for line in lines:
                        for first, hook in hooks.items():
                            if line.startswith(first):
                                updated = True
                                hook.update(line)
            else:
                updated = True

            if updated:
                print(''.join(w.render() for w in ws))
                sys.stdout.flush()
