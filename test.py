import msvcrt

while 1:
    print("running")
    if msvcrt.kbhit() and ord(msvcrt.getch()) == 27:
        aborted = True
        break
