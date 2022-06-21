import os
import time
import ctypes
import win32con as w32c
from pathlib import Path
from threading import Thread


import pyttsx3
from win32api import GetModuleHandle
from win32gui import (
    DestroyWindow, Shell_NotifyIcon,
    NIM_ADD, NIM_MODIFY, NIM_DELETE,
    UnregisterClass, CreateWindow, 
    WNDCLASS, RegisterClass,
    UpdateWindow, LoadImage,
    NIF_ICON, NIF_MESSAGE,
    NIF_TIP, NIF_INFO,
    PostQuitMessage)


class Announcer:
    
    def __init__(self, gender="female", rate: int=163):
        self._reader = pyttsx3.init()
        self.voices = self._reader.getProperty("voices")
        idx = -1 if gender == "female" else 0
        self._reader.setProperty("voices", self.voices[idx].id)
        self._reader.setProperty("rate", rate)

    def _adjust_spkrate(self, rate: int):
        return self._reader.setProperty("rate", rate)

    def _change_gender(self):
        voice = self._reader.getProperty("voice")
        if voice == self.voices[-1].id:
            return self._reader.setProperty("voice", self.voices[0].id)
        else:
            return self._reader.setProperty("voice", self.voices[-1].id)
        
    @property
    def spkrate(self):
        return self._reader.getProperty("rate")
    
    @property
    def gender(self):
        voice = self._reader.getProperty("voice")
        if voice == self.voices[-1].id:
            return "female"
        else:
            return "male"
        
    def announce(self, msg):
        self._reader.say(msg)
        self._reader.runAndWait()

    def variable_announce(self, msgs, pause=0.08):
        if type(msgs) == str:
            msgs = [msgs]
        for msg in msgs:
            self._change_gender()
            self.announce(msg)
            time.sleep(pause)
            
 
class Messenger(Announcer):
    
    def __init__(self):
        super().__init__()
        self.focus=[0x00, 0x100]
        self.parameters={
            "ok": {
                "btns": 0x0,
                "icon": 0x40},
            "yesno": {
                "btns": 0x04,
                "icon": 0x20},
            "okcancel": {
                "btns": 0x01,
                "icon": 0x10},
            "retrycancel": {
                "btns": 0x05,
                "icon": 0x30}}
        self.retcodes = {
            1: "ok",
            2: "cancel",
            4: "retry",
            6: "yes",
            7: "no"}
    
    def message(self, msg, title, btns="ok", focusbtn=0):
        if not focusbtn in [0, 1]:
            msg = "Defaulting Focus to 0."
            print(msg)
            focusbtn = 0
        btns_val = self.parameters[btns]["btns"]
        icon_val = self.parameters[btns]["icon"]
        focus_val = self.focus[focusbtn]
        return_code = ctypes.windll.user32.MessageBoxW(
            0, msg, title, btns_val | icon_val | focus_val)
        return self.retcodes[return_code]


class Notifyer(Messenger):
    
    def __init__(self, ico_path: os.PathLike=None):
        super().__init__()
        if not ico_path:
            ico_path = Path(Path(__file__).parent, "notifier.ico")
            print(ico_path)
        if not ico_path.exists():
            msg = "Ico path does not exist....\n"
            msg += "The notify function will not work without a .ico file "
            msg += "assigned to self.ico. The announce and message functions "
            msg += "are not impacted."
            print(ico_path)
            print(msg)
            self.ico = None
        else:
            self.ico = str(Path(ico_path))
    
    def _notify(self, msg, title, duration):
        wc = WNDCLASS()
        hinst = wc.hInstance = GetModuleHandle(None)
        wc.lpszClassName = f"{title} Notifyer"
        def OnDestroy(hwnd, msg, wparam, lparam):
            nid = (hwnd, 0)
            Shell_NotifyIcon(NIM_DELETE, nid)
            PostQuitMessage(0)
        message_map = {w32c.WM_DESTROY: OnDestroy}
        wc.lpfnWndProc = message_map
        classAtom = RegisterClass(wc)
        style = w32c.WS_OVERLAPPED | w32c.WS_SYSMENU
        hwnd = CreateWindow(classAtom, "Taskbar", style, \
                0, 0, w32c.CW_USEDEFAULT, w32c.CW_USEDEFAULT, \
                0, 0, hinst, None)
        UpdateWindow(hwnd)
        icon_flags = w32c.LR_LOADFROMFILE | w32c.LR_DEFAULTSIZE
        hicon = LoadImage(hinst, self.ico, w32c.IMAGE_ICON, 0, 0, icon_flags)
        flags = NIF_ICON | NIF_MESSAGE | NIF_TIP
        nid = (hwnd, 0, flags, w32c.WM_USER+20, hicon, "tooltip")
        Shell_NotifyIcon(NIM_ADD, nid)
        Shell_NotifyIcon(NIM_MODIFY, \
            (hwnd, 0, NIF_INFO, w32c.WM_USER+20,\
            hicon, "Notification", msg, 200, title))
        time.sleep(duration)
        DestroyWindow(hwnd)
        UnregisterClass(classAtom, hinst)
        
    def notify(self, msg, title, duration: int=3):
        if not self.ico:
            msg = ".notify() requires a .ico file assigned to self.ico"
            print(msg)
            return
        thrd = Thread(target=self._notify, args=(msg, title, duration,))
        thrd.start()
        time.sleep(duration)
        thrd.join()
