import winsound
from time import sleep

winsound.MessageBeep(winsound.MB_ICONHAND)  # Error
sleep(2)
winsound.MessageBeep(winsound.MB_ICONASTERISK)
sleep(2)
winsound.MessageBeep()
