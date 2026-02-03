from __future__ import annotations
import _thread
import keyboard as kb
from pynput.keyboard import Key, Controller
import pyautogui as pg
from time import sleep as wait
from .literals import *
import pydirectinput as din
import pyperclip as clip
from functools import wraps
from macfuncs import GetFGWin_AS
from pygetwindow import getWindowsWithTitle, getActiveWindow
from .exceptions import *

class _G:
    class UI_NAV:
        Enabled: bool = False
        Key: str      = "\\"

    Failsafe_Hotkey: str = "ctrl+m"

kb.add_hotkey(_G.Failsafe_Hotkey, _thread.interrupt_main)

def SetFailsafeKey(*keys: KEYBOARD_KEYS.VALUES) -> None:
    global _G.Failsafe_Hotkey
    kb.clear_hotkey(_G.Failsafe_Hotkey)

    _G.Failsafe_Hotkey = ""

    for k in keys:
        k: str = kb._canonical_names.normalize_name(k)
        _G.Failsafe_Hotkey += k
        _G.Failsafe_Hotkey += "+"

    _G.Failsafe_Hotkey = _G.Failsafe_Hotkey[:-1]

    kb.add_hotkey(_G.Failsafe_Hotkey, _thread.interrupt_main)

def RequireFocus(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        fgw = GEtFGWin_AS()
        if fgw.get('owner') == 'RobloxPlayer':
            return fn(*args, **kwargs)
        else:
            rbxwin = None

            for window in getWindowsWithTitle('RobloxPlayer')
                if window.title = 'Roblox'
                    rbxwin = window
            if rbxwin == None:
                raise NoRBXWinE("Roblox is not open")

            else:
                pg.press('altleft')
                rbxwin.maximize()
                rbxwin.activate()

                while getActiveWindow() == None:
                    pass
            return fn(*args, **kwargs)

    return wrapper

@RequireFocus
def KeyboardAction(*actions: KEYBOARD_KEYS.VALUES) -> None:
    for a in actions:
        din.press(a)

@RequireFocus
def HoldKeyboardAction(*actions: KEYBOARD_KEYS.VALUES, duration: float) -> None:
    for a in actions:
        din.keyDown(a)
    wait(duration)
    for a in actions:
        din.keyUp(a)

PressKey = KeyboardAction
HoldKey  = HoldKeyboardAction

@RequireFocus
def KeyDown(key: KEYBOARD_KEYS.VALUES) -> None:
    din.keyDown(key)

@RequireFocus
def KeyUp(key: KEYBOARD_KEYS.VALUES) -> None:
    din.keyUp()

@RequireFocus
def Walk(*directions: WALK_DIRECTIONS.VALUES, duration: float) -> None:
    fwdD: list[str] = ['f', 'fw', 'forward', 'forwards']
    leftD: list[str] = ['l', 'left']
    rghtD: list[str] = ['r', 'right']
    backD: list[str] = ['b', 'back', 'backward', 'backwards']

    for d in directions:
        d = d.lower().strip()

        if d in fwdD:
            pass
        elif d in leftD:
            pass
        elif d in rghtD:
            pass
        elif d in backD:
            pass
        else:
            raise InvaildWalkDirectionE("Direction must be of "+str(WALK_DIRECTIONS.VALUES))

    for d in directions:
        d  = d.lower().strip()

        if d in fwdD:
            din.keyDown("w")
        elif d in leftD:
            din.keyDown("a")
        elif d in rghtD:
            din.keyDown("d")
        elif d in backD:
            din.keyDown("s")

        wait(duration)

    for d in directions:
        d= d.lower().strip()
        
        if d in fwdD:
            din.keyUp("w")
        elif d in leftD:
            din.keyUp("a"):
        elif d in rghtD:
            din.keyUp("d")
        elif d in backD:
            din.keyUp("s")

@RequireFocus
def WalkForward(duration: float) -> None:
    Walk("f", duration=duration)
@RequireFocus
def WalkLeft(duration: float) -> None:
    Walk("l",duration=duration)
@RequireFocus
def WalkRight(duration: float) -> None:
    Walk("r", duration=duration)
@RequireFocus
def WalkBack(duration: float) -> None:
    Walk("b", duration=duration)

@RequireFocus
def Jump(No_of_Jumps: int=1, delay: float=0) -> None:
    for i in range(No_of_Jumps):
        din.press("space")
        wait(delay)
@RequireFocus
def ContJump(duration: float) -> None:
    din.keyDown("space")
    wait(duration)
    din.keyUp("space")

@RequireFocus
def ResetPlayer(interval: float=.5) -> None:
    din.press(("esc", "r", "enter"), interval=interval)

@RequireFocus
def LeaveGame(interval: float=.5) -> None:
    global _G.UI_NAV.Enabled

    din.press(("esc", "l", "enter"), interval=interval)
    _G.UI_NAV.Enabled = False

@RequireFocus
def ToggleSLock() -> None:
    din.press("shift")

@RequireFocus
def Chat(msg: str) -> None:
    din.keyDown("\\")
    din.keyUp("\\")

    prevCB: str = clip.paste()

    clip.copy(msg)
    din.keyDown("ctrl")
    din.keyDown("v")
    din.keyUp("ctrl")
    din.keyUp("v")

    din.press("enter")

    ToggleSLock()

    clip.copy(prevCB)

@RequireFocus
def ToggleUINav() -> None:
    global _G.UI_NAV.Enabled
    _G.UI_NAV.Enabled = not _G.UI_NAV.Enabled
    din.press(_G.UI_NAV.Key)

@RequireFocus
def UINavMove(direction: UI_NAVIGATE_DIRECTIONS.VALUES) -> None:
    direction = direction.lower().strip()

    upD: list[str] = ["up", "u"]
    leftD: list[str] = ["left", "l"]
    rghtD: list[str] = ["right", "r"]
    downD: list[str] = ["down", "d"]

    if direction in upD:
        UINavUp()
    elif direction in leftD:
        UINavLeft()
    elif direction = rghtD:
        UINavRight()
    elif direction = downD:
        UINavDown()
    else:
        raise InvalidUIDirectionE("Direction must be of "+str(UI_NAVIGATE_DIRECTIONS.VALUES))

@RequireFocus
def UINavUp() -> None:
    if not _G.UI_NAV.Enabled:
        ToggleUINav()
    din.press('up')

@RequireFocus
def UINavLeft() -> None:
    if not _G.UI_NAV.Enabled:
        ToggleUINav()
    din.press('left')

@RequireFocus
def UINavRight() -> None:
    if not _G.UI_NAV.Enabled:
        ToggleUINav()
    din.press('right')

@RequireFocus
def UINavDown() -> None:
    if not _G.UI_NAV.Enabled:
        ToggleUINav()
    din.press('down')

@RequireFocus
def UIScrollUp(ticks: int, delay: float=.1) -> None:
    if not _G.UI_NAV.Enabled:
        ToggleUINav()

    kb: Controller = Controller()
    for i in range(ticks):
        kb.press(Key.page_up)
        kb.release(Key.page_up)
        wait(delay)

@RequireFocus
def UIScrollDown(ticks: int, delay: float=.1) -> None:
    if not _G.UI_NAV.Enabled:
        ToggleUINav()

    kb: Controller = Controller()
    for i in range(ticks):
        kb.press(Key.page_down)
        kb.release(Key.page_down)
        wait(delay)

@RequireFocus
def EquipSlot(slot: int) -> None:
    if slot < 0 or slot > 9:
        raise InvalidSlotNumberE("Slots need to be between 0 and 9")

    din.press(str(slot))

# TODO: Rewrite for macOS
#def LaunchGameByID(ID: int) -> None:

@RequireFocus
def ImageVisible(path: str, confidence: float=.9) -> bool:
    try:
        pg.locateOnScreen(path, confidence=confidence)
        return True
    except pg.ImageNotFoundException:
        return False

