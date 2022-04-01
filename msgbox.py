import ctypes


BUTTONS={
    "ok": 0x0,
    "yes_no": 0x04,
    "ok_cancel": 0x01,
    "retry_cancel": 0x05,
    "yes_no_cancel": 0x03,
    "about_retry_ignore": 0x02,
    "cancel_tryagain_continue": 0x06}

ICONS={
    "!": 0x30, 
    "?": 0x20,
    "i": 0x40,
    "<>": 0x10}

FOCUSEDBUTTON={
    0: 0x00,
    1: 0x100,
    2: 0x200}

MODAL={

}

BEHAVIOR={
    
}

RES={
    1: "ok",
    2: "cancel",
    3: "abort",
    4: "retry",
    5: "ignore",
    6: "yes",
    7: "no",
    10: "tryagain",
    11: "continue"}


def msg(message: str, title: str="",
        button: str="ok", icon: str=None,
        button_focus_idx: int=0):
    if button_focus_idx > 2:
        print("Options for focused button:")
        print(FOCUSEDBUTTON)
        return
    if not icon:
        try:
            res=ctypes.windll.user32.MessageBoxW(
                    0,message,title,
                    BUTTONS[button]
                    |FOCUSEDBUTTON[button_focus_idx])
            return RES[res]
        except:
            print("Options for buttons:")
            print(BUTTONS.keys())
            return
    try:
        res=ctypes.windll.user32.MessageBoxW(
                0,message,title,
                BUTTONS[button]
                |ICONS[icon]
                |FOCUSEDBUTTON[button_focus_idx]) 
        return RES[res]
    except:
        print("Options for buttons:")
        print(BUTTONS.keys())
        print("Options for icons:")
        print(ICONS.keys())
