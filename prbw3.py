from __future__ import annotations
import signal
import sys
from pynput.keyboard import Key, Controller, Listener
import pyautogui as pg
from time import sleep as wait
from literals import *
import pyperclip as clip
from functools import wraps
from macfuncs import GetFGWin_AS
from AppKit import NSWorkspace
import subprocess
from exceptions import *

# Global variables
UINAVENABLED: bool = False
UINAVKEY: str = "\\"
FAILSAFE: list[str] = ["ctrl", "m"]  # Store as list instead of string

# Initialize keyboard controller
keyboard = Controller()

# Global listener for failsafe
failsafe_listener = None

def handle_failsafe(key):
    """Handle failsafe key combination"""
    # This would need to track key states
    # For simplicity, we'll use a different approach
    pass

def SetFailsafeKey(*keys: KEYBOARD_KEYS.VALUES) -> None:
    global FAILSAFE
    FAILSAFE = list(keys)

def RequireFocus(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        fgw = GetFGWin_AS()
        if fgw.get('owner') == 'RobloxPlayer':
            return fn(*args, **kwargs)
        else:
            # macOS specific window activation
            try:
                # Use AppleScript to activate Roblox
                applescript = '''
                tell application "System Events"
                    set robloxProcess to first application process whose name is "RobloxPlayer"
                    if robloxProcess exists then
                        set frontmost of robloxProcess to true
                    else
                        error "Roblox is not running"
                    end if
                end tell
                '''
                
                subprocess.run(['osascript', '-e', applescript], check=True)
                
                # Wait for Roblox to become active
                max_wait = 5
                waited = 0
                while waited < max_wait:
                    active_app = NSWorkspace.sharedWorkspace().activeApplication()
                    if active_app.get('NSApplicationName') == 'RobloxPlayer':
                        break
                    wait(0.5)
                    waited += 0.5
                
                if waited >= max_wait:
                    raise NoRBXWinE("Could not activate Roblox window")
                    
            except subprocess.CalledProcessError:
                raise NoRBXWinE("Roblox is not open")
            except Exception as e:
                raise NoRBXWinE(f"Error activating Roblox: {str(e)}")
                
            return fn(*args, **kwargs)

    return wrapper

@RequireFocus
def KeyboardAction(*actions: KEYBOARD_KEYS.VALUES) -> None:
    for a in actions:
        keyboard.press(a)
        keyboard.release(a)

@RequireFocus
def HoldKeyboardAction(*actions: KEYBOARD_KEYS.VALUES, duration: float) -> None:
    for a in actions:
        keyboard.press(a)
    wait(duration)
    for a in actions:
        keyboard.release(a)

PressKey = KeyboardAction
HoldKey = HoldKeyboardAction

@RequireFocus
def KeyDown(key: KEYBOARD_KEYS.VALUES) -> None:
    keyboard.press(key)

@RequireFocus
def KeyUp(key: KEYBOARD_KEYS.VALUES) -> None:
    keyboard.release(key)

@RequireFocus
def Walk(*directions: WALK_DIRECTIONS.VALUES, duration: float) -> None:
    fwdD: list[str] = ['f', 'fw', 'forward', 'forwards']
    leftD: list[str] = ['l', 'left']
    rghtD: list[str] = ['r', 'right']
    backD: list[str] = ['b', 'back', 'backward', 'backwards']

    # Validate directions
    for d in directions:
        d = d.lower().strip()
        if not (d in fwdD or d in leftD or d in rghtD or d in backD):
            raise InvaildWalkDirectionE("Direction must be of " + str(WALK_DIRECTIONS.VALUES))

    keys_to_press = []
    
    # Determine which keys to press
    for d in directions:
        d = d.lower().strip()
        if d in fwdD:
            keys_to_press.append('w')
        elif d in leftD:
            keys_to_press.append('a')
        elif d in rghtD:
            keys_to_press.append('d')
        elif d in backD:
            keys_to_press.append('s')
    
    # Press all keys
    for key in keys_to_press:
        keyboard.press(key)
    
    wait(duration)
    
    # Release all keys
    for key in keys_to_press:
        keyboard.release(key)

@RequireFocus
def WalkForward(duration: float) -> None:
    Walk("f", duration=duration)

@RequireFocus
def WalkLeft(duration: float) -> None:
    Walk("l", duration=duration)

@RequireFocus
def WalkRight(duration: float) -> None:
    Walk("r", duration=duration)

@RequireFocus
def WalkBack(duration: float) -> None:
    Walk("b", duration=duration)

@RequireFocus
def Jump(No_of_Jumps: int = 1, delay: float = 0) -> None:
    for i in range(No_of_Jumps):
        keyboard.press(Key.space)
        keyboard.release(Key.space)
        wait(delay)

@RequireFocus
def ContJump(duration: float) -> None:
    keyboard.press(Key.space)
    wait(duration)
    keyboard.release(Key.space)

@RequireFocus
def ResetPlayer(interval: float = .5) -> None:
    keyboard.press(Key.esc)
    keyboard.release(Key.esc)
    wait(interval)
    keyboard.press('r')
    keyboard.release('r')
    wait(interval)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

@RequireFocus
def LeaveGame(interval: float = .5) -> None:
    global UINAVENABLED

    keyboard.press(Key.esc)
    keyboard.release(Key.esc)
    wait(interval)
    keyboard.press('l')
    keyboard.release('l')
    wait(interval)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
    UINAVENABLED = False

@RequireFocus
def ToggleSLock() -> None:
    # Shift lock on macOS
    keyboard.press(Key.shift_l)
    keyboard.release(Key.shift_l)

@RequireFocus
def Chat(msg: str, chat_coords: tuple[float, float] = (71.3984375, 350.1015625)) -> None:
    """
    Send a chat message by clicking on the chat input box
    
    Args:
        msg: Message to send
        chat_coords: Coordinates of the chat input box (x, y)
    """
    try:
        # Save current clipboard
        prevCB: str = clip.paste()
        
        # Copy message to clipboard
        clip.copy(msg)
        
        # Move to chat input box and click
        pg.moveTo(chat_coords[0], chat_coords[1], duration=0.3)
        pg.click()
        wait(0.2)  # Wait for chat to activate
        
        # Paste using Command+V on macOS
        with keyboard.pressed(Key.cmd):
            keyboard.press('v')
            keyboard.release('v')
        
        # Send message
        wait(0.1)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        
        # Optional: Toggle shift lock
        # ToggleSLock()
        
        # Restore clipboard after a short delay
        wait(0.2)
        clip.copy(prevCB)
        
    except Exception as e:
        print(f"Error in Chat function: {e}")
        # Fallback to typing method
        type_chat_fallback(msg)

def type_chat_fallback(msg: str) -> None:
    """Fallback method: type message directly"""
    try:
        # Type each character
        for char in msg:
            if char == ' ':
                keyboard.press(Key.space)
                keyboard.release(Key.space)
            elif char == '\n':
                with keyboard.pressed(Key.shift):
                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter)
            else:
                keyboard.press(char)
                keyboard.release(char)
            wait(0.01)
        
        # Send message
        wait(0.1)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        
    except Exception as e:
        print(f"Fallback chat also failed: {e}")

@RequireFocus 
def ClickChat(coords: tuple[float, float] = (71.3984375, 350.1015625)) -> None:
    """Just click on the chat input box without sending a message"""
    pg.moveTo(coords[0], coords[1], duration=0.3)
    pg.click()
    wait(0.2)
    print(f"Clicked chat at ({coords[0]}, {coords[1]})")

@RequireFocus
def FindChatCoordinates() -> tuple[float, float]:
    """Helper function to find chat coordinates interactively"""
    print("Move your mouse to the chat input box...")
    print("Press Enter when ready, or wait 10 seconds...")
    
    import threading
    
    coords = None
    stop_event = threading.Event()
    
    def get_coordinates():
        nonlocal coords
        while not stop_event.is_set():
            coords = pg.position()
            wait(0.1)
    
    # Start thread to track mouse position
    tracker = threading.Thread(target=get_coordinates)
    tracker.start()
    
    try:
        # Wait for Enter or timeout
        input_thread = threading.Thread(target=input, args=("",))
        input_thread.daemon = True
        input_thread.start()
        
        # Wait 10 seconds max
        input_thread.join(timeout=10)
        
    except:
        pass
    finally:
        stop_event.set()
        tracker.join()
    
    if coords:
        print(f"\nChat coordinates found: {coords}")
        return coords
    else:
        print("\nUsing default coordinates")
        return (71.3984375, 350.1015625)

@RequireFocus
def TestChatCoordinates() -> None:
    """Test if the current chat coordinates are correct"""
    test_coords = FindChatCoordinates()
    
    print(f"\nTesting chat at coordinates: {test_coords}")
    print("Will test in 3 seconds...")
    wait(3)
    
    # Test click
    ClickChat(test_coords)
    
    # Test sending a message
    test_msg = "Chat test 123"
    print(f"Sending test message: '{test_msg}'")
    Chat(test_msg, test_coords)
    
    print("\nDid the chat work correctly?")
    print("If not, try finding new coordinates with FindChatCoordinates()")

# Update the main Chat function with more options
@RequireFocus
def ChatAdvanced(msg: str, 
                 chat_coords: tuple[float, float] = (71.3984375, 350.1015625),
                 method: str = "click",  # "click" or "keyboard"
                 chat_key: str = "/",
                 use_clipboard: bool = True) -> None:
    """
    Advanced chat function with multiple methods
    
    Args:
        msg: Message to send
        chat_coords: Coordinates for click method
        method: "click" or "keyboard"
        chat_key: Keyboard key to open chat (for keyboard method)
        use_clipboard: Use clipboard paste or type directly
    """
    if method == "click":
        Chat(msg, chat_coords)
    else:
        # Keyboard method
        if use_clipboard:
            prevCB = clip.paste()
            clip.copy(msg)
            
            # Press chat key
            if chat_key == 'enter':
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)
            else:
                keyboard.press(chat_key)
                keyboard.release(chat_key)
            
            wait(0.3)
            
            # Paste
            with keyboard.pressed(Key.cmd):
                keyboard.press('v')
                keyboard.release('v')
            
            # Send
            wait(0.1)
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
            
            wait(0.2)
            clip.copy(prevCB)
        else:
            # Type directly
            if chat_key == 'enter':
                keyboard.press(Key.enter)
                keyboard.release(Key.enter)
            else:
                keyboard.press(chat_key)
                keyboard.release(chat_key)
            
            wait(0.3)
            
            for char in msg:
                if char == ' ':
                    keyboard.press(Key.space)
                    keyboard.release(Key.space)
                elif char == '\n':
                    with keyboard.pressed(Key.shift):
                        keyboard.press(Key.enter)
                        keyboard.release(Key.enter)
                else:
                    try:
                        keyboard.press(char)
                        keyboard.release(char)
                    except:
                        with keyboard.pressed(Key.shift):
                            keyboard.press(char)
                            keyboard.release(char)
                wait(0.01)
            
            wait(0.1)
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)

@RequireFocus
def ToggleUINav() -> None:
    global UINAVENABLED, UINAVKEY
    UINAVENABLED = not UINAVENABLED

    if UINAVKEY == "\\":
        keyboard.press('\\')
        keyboard.release('\\')
    else:
        keyboard.press(UINAVKEY)
        keyboard.release(UINAVKEY)

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
    elif direction in rghtD:
        UINavRight()
    elif direction in downD:
        UINavDown()
    else:
        raise InvalidUIDirectionE("Direction must be of " + str(UI_NAVIGATE_DIRECTIONS.VALUES))

@RequireFocus
def UINavUp() -> None:
    global UINAVENABLED
    if not UINAVENABLED:
        ToggleUINav()

    keyboard.press(Key.up)
    keyboard.release(Key.up)

@RequireFocus
def UINavLeft() -> None:
    global UINAVENABLED
    if not UINAVENABLED:
        ToggleUINav()

    keyboard.press(Key.left)
    keyboard.release(Key.left)

@RequireFocus
def UINavRight() -> None:
    global UINAVENABLED
    if not UINAVENABLED:
        ToggleUINav()
    
    keyboard.press(Key.right)
    keyboard.release(Key.right)

@RequireFocus
def UINavDown() -> None:
    global UINAVENABLED
    if not UINAVENABLED:
        ToggleUINav()
    
    keyboard.press(Key.down)
    keyboard.release(Key.down)

@RequireFocus
def UIScrollUp(ticks: int, delay: float = .1) -> None:
    global UINAVENABLED
    if not UINAVENABLED:
        ToggleUINav()

    for i in range(ticks):
        keyboard.press(Key.page_up)
        keyboard.release(Key.page_up)
        wait(delay)

@RequireFocus
def UIScrollDown(ticks: int, delay: float = .1) -> None:
    global UINAVENABLED
    if not UINAVENABLED:
        ToggleUINav()

    for i in range(ticks):
        keyboard.press(Key.page_down)
        keyboard.release(Key.page_down)
        wait(delay)

@RequireFocus
def EquipSlot(slot: int) -> None:
    if slot < 0 or slot > 9:
        raise InvalidSlotNumberE("Slots need to be between 0 and 9")

    keyboard.press(str(slot))
    keyboard.release(str(slot))

@RequireFocus
def LaunchGameByID(ID: int) -> None:
    """Launch Roblox game by ID on macOS"""
    try:
        # Construct Roblox URL
        roblox_url = f"roblox://placeID={ID}"
        
        # Open the URL using open command
        subprocess.run(['open', roblox_url], check=True)
        
        # Wait for game to load
        wait(10)  # Wait 10 seconds for game to load
        
        # Try to activate the window
        applescript = '''
        tell application "System Events"
            set robloxProcess to first application process whose name is "RobloxPlayer"
            set frontmost of robloxProcess to true
        end tell
        '''
        subprocess.run(['osascript', '-e', applescript], check=True)
        
    except subprocess.CalledProcessError as e:
        raise NoRBXWinE(f"Failed to launch game: {str(e)}")
    except Exception as e:
        raise NoRBXWinE(f"Error launching game: {str(e)}")

@RequireFocus
def ImageVisible(path: str, confidence: float = .9) -> bool:
    try:
        pg.locateOnScreen(path, confidence=confidence)
        return True
    except pg.ImageNotFoundException:
        return False

# macOS specific functions
def GetActiveAppName() -> str:
    """Get the name of the currently active application"""
    active_app = NSWorkspace.sharedWorkspace().activeApplication()
    return active_app.get('NSApplicationName', '')

def IsRobloxFocused() -> bool:
    """Check if Roblox is currently focused"""
    return GetActiveAppName() == 'RobloxPlayer'

def FocusRoblox() -> bool:
    """Try to focus Roblox window"""
    try:
        applescript = '''
        tell application "System Events"
            set robloxProcess to first application process whose name is "RobloxPlayer"
            set frontmost of robloxProcess to true
        end tell
        '''
        subprocess.run(['osascript', '-e', applescript], check=True)
        return True
    except:
        return False

def install_failsafe_handler():
    """Install a signal-based failsafe handler"""
    def signal_handler(sig, frame):
        print("\nFailsafe triggered! Exiting...")
        sys.exit(0)
    
    # Use Ctrl+C as failsafe
    signal.signal(signal.SIGINT, signal_handler)
    print("Failsafe: Press Ctrl+C to stop the script")

# Install the signal handler
install_failsafe_handler()
