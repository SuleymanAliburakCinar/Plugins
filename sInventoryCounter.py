from phBot import *
from threading import Timer
from time import sleep
import phBotChat
import QtBind
import struct
import random
import json
import os
import time

pName = 'sInventoryCounter'
pVersion = '1.0'
pUrl = "https://raw.githubusercontent.com/SuleymanAliburakCinar/Plugins/master/sInventoryCounter.py"

# ______________________________ Initializing ______________________________ #

# Graphic user interface
gui = QtBind.init(__name__, pName)

tbxLeaders = QtBind.createLineEdit(gui, "", 511, 11, 100, 20)
lstLeaders = QtBind.createList(gui, 511, 32, 176, 48)
btnAddLeader = QtBind.createButton(gui, 'btnAddLeader_clicked', "    Add    ", 612, 10)
btnRemLeader = QtBind.createButton(gui, 'btnRemLeader_clicked', "     Remove     ", 560, 79)

qm = "'"

QtBind.createLabel(gui,'Type commands from the attached leader to check your entire party'+qm+'s inventory',12,12)
QtBind.createLabel(gui, 'Command List:\n\ninv :\t Check the empty slots of the entire party'+qm+'s inventory\ngold :\t Check the gold of the whole party\nexp :\t Check the level and exp of the whole party\npouch :\t Check the pouch of the whole party (Specialty)\nlamp :\t Check the lamps in the inventory  of the whole party\nsox :\t Check the sox items in your inventory. (except your gear) \n\n(w,a,s,acc) : Use one of the commands to check the elixirs in your inventory.', 15, 45)


# ______________________________ Methods ______________________________ #

# Return xControl folder path
def getPath():
    return get_config_dir() + pName + "\\"


# Return character configs path (JSON)
def getConfig():
    return getPath() + inGame['server'] + "_" + inGame['name'] + ".json"


# Check if character is ingame
def isJoined():
    global inGame
    inGame = get_character_data()
    if not (inGame and "name" in inGame and inGame["name"]):
        inGame = None
    return inGame


# Load default configs
def loadDefaultConfig():
    # Clear data
    QtBind.clear(gui, lstLeaders)


# Loads all config previously saved
def loadConfigs():
    loadDefaultConfig()
    if isJoined():
        # Check config exists to load
        if os.path.exists(getConfig()):
            data = {}
            with open(getConfig(), "r") as f:
                data = json.load(f)
            if "Leaders" in data:
                for nickname in data["Leaders"]:
                    QtBind.append(gui, lstLeaders, nickname)

# Add leader to the list
def btnAddLeader_clicked():
    if inGame:
        player = QtBind.text(gui, tbxLeaders)
        # Player nickname it's not empty
        if player and not lstLeaders_exist(player):
            # Init dictionary
            data = {}
            # Load config if exist
            if os.path.exists(getConfig()):
                with open(getConfig(), 'r') as f:
                    data = json.load(f)
            # Add new leader
            if not "Leaders" in data:
                data['Leaders'] = []
            data['Leaders'].append(player)

            # Replace configs
            with open(getConfig(), "w") as f:
                f.write(json.dumps(data, indent=4, sort_keys=True))
            QtBind.append(gui, lstLeaders, player)
            QtBind.setText(gui, tbxLeaders, "")
            log('Plugin: Leader added [' + player + ']')


# Remove leader selected from list
def btnRemLeader_clicked():
    if inGame:
        selectedItem = QtBind.text(gui, lstLeaders)
        if selectedItem:
            if os.path.exists(getConfig()):
                data = {"Leaders": []}
                with open(getConfig(), 'r') as f:
                    data = json.load(f)
                try:
                    # remove leader nickname from file if exists
                    data["Leaders"].remove(selectedItem)
                    with open(getConfig(), "w") as f:
                        f.write(json.dumps(data, indent=4, sort_keys=True))
                except:
                    pass  # just ignore file if doesn't exist
            QtBind.remove(gui, lstLeaders, selectedItem)
            log('Plugin: Leader removed [' + selectedItem + ']')


# Return True if nickname exist at the leader list
def lstLeaders_exist(nickname):
    nickname = nickname.lower()
    players = QtBind.getItems(gui, lstLeaders)
    for i in range(len(players)):
        if players[i].lower() == nickname:
            return True
    return False


def handleChatCommand(msg):
    # Try to split message
    args = msg.split(' ', 1)
    # Check if the format is correct and is not empty
    if len(args) != 2 or not args[0] or not args[1]:
        return
    # Split correctly the message
    t = args[0].lower()
    if t == 'private' or t == 'note':
        # then check message is not empty
        argsExtra = args[1].split(' ', 1)
        if len(argsExtra) != 2 or not argsExtra[0] or not argsExtra[1]:
            return
        args.pop(1)
        args += argsExtra
    # Check message type
    sent = False
    if t == "all":
        sent = phBotChat.All(args[1])
    elif t == "private":
        sent = phBotChat.Private(args[1], args[2])
    elif t == "party":
        sent = phBotChat.Party(args[1])
    elif t == "guild":
        sent = phBotChat.Guild(args[1])
    elif t == "union":
        sent = phBotChat.Union(args[1])
    elif t == "note":
        sent = phBotChat.Note(args[1], args[2])
    elif t == "stall":
        sent = phBotChat.Stall(args[1])
    elif t == "global":
        sent = phBotChat.Global(args[1])
    if sent:
        log('Plugin: Message "' + t + '" sent successfully!')


def checkInv(arg):
    weapon = 0
    protector = 0
    accessory = 0
    shield = 0
    lamp = 0
    dLamp = 0
    sunItems = 0
    items = []
    items = get_inventory()['items'][13:]

    if items:
        for item in items:
            if item is not None:
                # log(item["name"])
                if "Lv.11" in item['name'] and "(Weapon)" in item['name']:
                    weapon += item['quantity']
                if "Lv.11" in item['name'] and "(Armor)" in item['name']:
                    protector += item['quantity']
                if "Lv.11" in item['name'] and "(Accessory)" in item['name']:
                    accessory += item['quantity']
                if "Lv.11" in item['name'] and "(Shield)" in item['name']:
                    shield += item['quantity']
                if "Genie’s Lamp" in item['name']:
                    lamp += item['quantity']
                if "Dirty Lamp" in item['name']:
                    dLamp += item['quantity']
                if 'RARE' in item['servername'] and 'EVENT' not in item['servername'] and 'ARCHEMY' not in item[
                    'servername']:
                    sunItems += 1

    pets = get_pets()

    if pets != []:
        for p in pets.keys():
            pet = pets[p]
            if pet['type'] in 'pick':
                for petItems in pet['items']:
                    if petItems != None:
                        if "Lv.11" in petItems['name'] and "(Weapon)" in petItems['name']:
                            weapon += petItems['quantity']
                        if "Lv.11" in petItems['name'] and "(Armor)" in petItems['name']:
                            protector += petItems['quantity']
                        if "Lv.11" in petItems['name'] and "(Accessory)" in petItems['name']:
                            accessory += petItems['quantity']
                        if "Lv.11" in petItems['name'] and "(Shield)" in petItems['name']:
                            shield += petItems['quantity']
                        if "Genie’s Lamp" in petItems['name']:
                            lamp += petItems['quantity']
                        if "Dirty Lamp" in petItems['name']:
                            dLamp += petItems['quantity']
                        if 'RARE' in petItems['servername'] and 'EVENT' not in petItems[
                            'servername'] and 'ARCHEMY' not in petItems['servername']:
                            sunItems += 1

    if arg == "Weapon":
        handleChatCommand("party Weapon " + str(weapon))
    if arg == "Armor":
        handleChatCommand("party Armor " + str(protector))
    if arg == "Accessory":
        handleChatCommand("party Accessory " + str(accessory))
    if arg == "Shield":
        handleChatCommand("party Shield " + str(shield))
    if arg == "Lamp":
        handleChatCommand("party Genie’s Lamp " + str(lamp) + " -- Dirty Lamp " + str(dLamp))
    if arg == "Sox":
        handleChatCommand("party " + str(sunItems) + " parts Sox item")


def checkGold():
    gold = 0;

    chars = []
    chars = get_character_data()

    if chars != []:
        gold += chars['gold']

    goldS = format(gold, ",")

    handleChatCommand("party Gold " + str(goldS))


def checkExp():
    data = get_character_data()
    currentExp = data['current_exp']
    level = data['level']
    maxExp = data['max_exp']
    exp = float((100 * currentExp) / maxExp)

    handleChatCommand("party Level: " + str(level) + " - Exp: %" + str("{:.2f}".format(exp)))


def ınventorySpace():
    size = 0
    usingSpace = 0

    items = []
    items = get_inventory()['items'][12:]
    size = get_inventory()['size'] - 12

    if items != []:
        for item in items:
            if item != None:
                usingSpace += 1

    size -= 1
    usingSpace -= 1
    handleChatCommand("party Empty Space " + str(size - usingSpace) + "  ---->  " + str(usingSpace) + "/" + str(size))


def specialtyGoodsBox():
    i = 0
    j = 0
    pouch = get_job_pouch()
    items = []
    items = get_job_pouch()["items"]
    if items != []:
        for item in items:
            j = j + 1
            if item is not None:
                i = i + item["quantity"]

    handleChatCommand("party Specialty -> " + str(i) + " / " + str(j * 5))


def checkGuild():
    items = []
    items = get_guild_storage()['items']

    sunItems = [0 for i in range(11)]
    moonItems = [0 for i in range(10)]
    sosItems = [0 for i in range(10)]

    if items != []:
        for item in items:
            if item != None:
                if 'RARE' in item['servername'] and 'EVENT' not in item['servername'] and 'ARCHEMY' not in item[
                    'servername']:
                    # split = item['servername'].split('_')
                    log(item['servername'])
                    # dg = int(str(split[4]))
                    dg = [int(s) for s in item['servername'].split('_') if s.isdigit()][0]
                    if dg < 11:
                        if '_C_' in item['servername']:
                            sunItems[dg - 1] += 1
                        elif '_B_' in item['servername']:
                            moonItems[dg - 1] += 1
                        elif '_A_' in item['servername']:
                            sosItems[dg - 1] += 1
                    else:
                        if '_A_' in item['servername']:
                            sunItems[10] += 1

    i = 1
    for x in sunItems:
        log(str(i) + " " + str(x) + "\t")
        i = i + 1


# ______________________________ Events ______________________________ #

# Called when the bot successfully connects to the game server
def connected():
    global inGame
    inGame = None


# Called when the character enters the game world
def joined_game():
    loadConfigs()


# All chat messages received are sent to this function
def handle_chat(t, player, msg):
    i = 0;
    j = 0;
    k = 0;
    l = 0;
    # Check player at leader list or a Discord message
    if player and lstLeaders_exist(player) or t == 100:

        if msg == "w":
            checkInv("Weapon")
        elif msg == "a":
            checkInv("Armor")
        elif msg == "s":
            checkInv("Shield")
        elif msg == "acc":
            checkInv("Accessory")
        elif msg == "lamp":
            checkInv("Lamp")
        elif msg == "gold":
            checkGold()
        elif msg == "inv":
            ınventorySpace()
        elif msg == "pouch":
            specialtyGoodsBox()
        elif msg == "G":
            checkGuild()
        elif msg == "sox":
            checkInv("Sox")
        elif msg == "exp":
            checkExp()


# Called every 500ms
# def event_loop():


# Plugin loaded
log("Plugin: " + pName + " v" + pVersion + " successfully loaded")

if os.path.exists(getPath()):
    # Adding RELOAD plugin support
    loadConfigs()
else:
    # Creating configs folder
    os.makedirs(getPath())
    log('Plugin: ' + pName + ' folder has been created')
