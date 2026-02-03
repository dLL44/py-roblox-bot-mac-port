import subprocess

def GetFGWin_AS():
    script = r'''
    tell application "System Events"
        set frontProc to first application process whose frontmost is true
        set appName to name of frontProc
        set winTitle to ""
        try
            set winTitle to name of front window of frontProc
        end try
        return appName & "||" & winTitle
    end tell
    '''
    out = subprocess.check_output(["osascript", "-e", script]).decode("utf-8").strip()
    app, title = (out.split("||", 1) + [""])[:2]
    return {"owner": app, "title": title}

while True:
    win = GetFGWin_AS()
    print(win)
    if win.get('owner') == 'RobloxPlayer':
        print("Found Roblox")
        break

