import i3ipc

i3 = i3ipc.Connection()
def nothing():
    return "nothjign"
i3.on('workspace::focus', nothing) 
i3.main()
