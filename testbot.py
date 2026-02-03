import prbw3 as bot
from time import sleep as wait

print("Running bot in 5 seconds.")
wait(5)
bot.Chat("Roblox Automation Test using prbw3 - a macOS rewrite of py-roblox-bot. Made by bleedingiv on .gg and roblox")

wd: float = .3

wait(2)

bot.Chat("Testing walks w/o ShiftLock...")
bot.WalkForward(wd)
bot.WalkBack(wd)
wait(1)
bot.WalkBack(wd)
bot.WalkForward(wd)
wait(wd)
bot.WalkLeft(wd)
bot.WalkRight(wd)
wait(wd)
bot.WalkRight(wd)
bot.WalkLeft(wd)

bot.Chat("Testing walks with ShiftLock")
bot.ToggleSLock()
bot.WalkForward(wd)
bot.WalkBack(wd)
wait(1)
bot.WalkBack(wd)
bot.WalkForward(wd)
wait(wd)
bot.WalkLeft(wd)
bot.WalkRight(wd)
wait(1)
bot.WalkRight(wd)
bot.WalkLeft(wd)
bot.ToggleSLock()

bot.Chat("Testing jumps...")
bot.Jump(3, .3)
wait(1)

bot.Chat("Movement Tests Done, running UI Navigation and Inventory.")

print("Inventory Check")
for s in range(1,4):
    bot.EquipSlot(s)
    wait(.5)


print("UI Navigation Check")
bot.ToggleUINav()
bot.UINavUp()
bot.UINavDown()
bot.UINavLeft()
bot.UINavRight()
bot.ToggleUINav()

bot.Chat("Finished! You can find prbw3 soon, or msg me for beta access!")
