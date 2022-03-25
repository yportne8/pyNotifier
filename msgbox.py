import ctypes


def msg(title: str, message: str,
            button: str="OK", icon: str=None,
            ismodal=True):
    buttons={
        "OK":0x0,
        "OKCXL":0x01,
        "YESNOCXL":0x03,
        "YESNO":0x04,
        "HELP":0x4000}
    button=buttons[button]
    if icon:
        icons={
            "!":0x30, 
            "?":0x40,
            "<>":0x10}
        icon=icons[icon]
    if ismodal:
        modal:4096
    try:
        ctypes.windll.user32.MessageBoxW(
            0,message,title, button | icon | modal)
    except:
        try:
            ctypes.windll.user32.MessageBoxW(
                0,message,title, button | icon)
        except:
            try:
                ctypes.windll.user32.MessageBoxW(
                    0,message,title, button | modal)
            except:
                try:
                    ctypes.windll.user32.MessageBoxW(
                        0, message,title, button)
            
                except Exception as e:
                    print("Failed:")
                    print(str(e))