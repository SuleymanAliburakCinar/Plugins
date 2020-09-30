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

pName = 'sElixirCounter'
pVersion = '0.1'



# ______________________________ Initializing ______________________________ #

# Graphic user interface
gui = QtBind.init(__name__,pName)

tbxLeaders = QtBind.createLineEdit(gui,"",511,11,100,20)
lstLeaders = QtBind.createList(gui,511,32,176,48)
btnAddLeader = QtBind.createButton(gui,'btnAddLeader_clicked',"    Add    ",612,10)
btnRemLeader = QtBind.createButton(gui,'btnRemLeader_clicked',"     Remove     ",560,79)

lSack = QtBind.createLabel(gui,'0 / 0',11,10)

# ______________________________ Methods ______________________________ #

# Return xControl folder path
def getPath():
	return get_config_dir()+pName+"\\"

# Return character configs path (JSON)
def getConfig():
	return getPath()+inGame['server'] + "_" + inGame['name'] + ".json"

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
	QtBind.clear(gui,lstLeaders)

# Loads all config previously saved
def loadConfigs():
	loadDefaultConfig()
	if isJoined():
		# Check config exists to load
		if os.path.exists(getConfig()):
			data = {}
			with open(getConfig(),"r") as f:
				data = json.load(f)
			if "Leaders" in data:
				for nickname in data["Leaders"]:
					QtBind.append(gui,lstLeaders,nickname)

# Add leader to the list
def btnAddLeader_clicked():
	if inGame:
		player = QtBind.text(gui,tbxLeaders)
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
			with open(getConfig(),"w") as f:
				f.write(json.dumps(data, indent=4, sort_keys=True))
			QtBind.append(gui,lstLeaders,player)
			QtBind.setText(gui, tbxLeaders,"")
			log('Plugin: Leader added ['+player+']')

# Remove leader selected from list
def btnRemLeader_clicked():
	if inGame:
		selectedItem = QtBind.text(gui,lstLeaders)
		if selectedItem:
			if os.path.exists(getConfig()):
				data = {"Leaders":[]}
				with open(getConfig(), 'r') as f:
					data = json.load(f)
				try:
					# remove leader nickname from file if exists
					data["Leaders"].remove(selectedItem)
					with open(getConfig(),"w") as f:
						f.write(json.dumps(data, indent=4, sort_keys=True))
				except:
					pass # just ignore file if doesn't exist
			QtBind.remove(gui,lstLeaders,selectedItem)
			log('Plugin: Leader removed ['+selectedItem+']')

# Return True if nickname exist at the leader list
def lstLeaders_exist(nickname):
	nickname = nickname.lower()
	players = QtBind.getItems(gui,lstLeaders)
	for i in range(len(players)):
		if players[i].lower() == nickname:
			return True
	return False


def handleChatCommand(msg):
	# Try to split message
	args = msg.split(' ',1)
	# Check if the format is correct and is not empty
	if len(args) != 2 or not args[0] or not args[1]:
		return
	# Split correctly the message
	t = args[0].lower()
	if t == 'private' or t == 'note':
		# then check message is not empty
		argsExtra = args[1].split(' ',1)
		if len(argsExtra) != 2 or not argsExtra[0] or not argsExtra[1]:
			return
		args.pop(1)
		args += argsExtra
	# Check message type
	sent = False
	if t == "all":
		sent = phBotChat.All(args[1])
	elif t == "private":
		sent = phBotChat.Private(args[1],args[2])
	elif t == "party":
		sent = phBotChat.Party(args[1])
	elif t == "guild":
		sent = phBotChat.Guild(args[1])
	elif t == "union":
		sent = phBotChat.Union(args[1])
	elif t == "note":
		sent = phBotChat.Note(args[1],args[2])
	elif t == "stall":
		sent = phBotChat.Stall(args[1])
	elif t == "global":
		sent = phBotChat.Global(args[1])
	if sent:
		log('Plugin: Message "'+t+'" sent successfully!')

def checkElixir(arg):

	weapon = 0;
	protector = 0;
	accessory = 0;
	shield = 0;

	items = []
	items = get_inventory()['items']

	if items != []:
		for item in items:
			if item != None:
				#log(item["name"])
				if "Lv.10" in item['name'] and "(Weapon)" in item['name']:
					weapon += item['quantity']
				if "Lv.10" in item['name'] and "(Armor)" in item['name']:
					protector += item['quantity']
				if "Lv.10" in item['name'] and "(Accessory)" in item['name']:
					accessory += item['quantity']
				if "Lv.10" in item['name'] and "(Shield)" in item['name']:
					shield += item['quantity']
	if arg == "Weapon":
		handleChatCommand("party Weapon "+str(weapon))
	if arg == "Armor":
		handleChatCommand("party Armor "+str(protector))
	if arg == "Accessory":
		handleChatCommand("party Accessory "+str(accessory))
	if arg == "Shield":
		handleChatCommand("party Shield "+str(shield))


# ______________________________ Events ______________________________ #

# Called when the bot successfully connects to the game server
def connected():
	global inGame
	inGame = None

# Called when the character enters the game world
def joined_game():
	loadConfigs()

# All chat messages received are sent to this function
def handle_chat(t,player,msg):
	i = 0;
	j = 0;
	k = 0;
	l = 0;
	# Check player at leader list or a Discord message
	if player and lstLeaders_exist(player) or t == 100:

		if msg == "W":
			checkElixir("Weapon")
		elif msg == "A":
			checkElixir("Armor")
		elif msg == "S":
			checkElixir("Shield")
		elif msg == "Acc":
			checkElixir("Accessory")

# Called every 500ms
#def event_loop():


# Plugin loaded
log("Plugin: "+pName+" v"+pVersion+" successfully loaded")

if os.path.exists(getPath()):
	# Adding RELOAD plugin support
	loadConfigs()
else:
	# Creating configs folder
	os.makedirs(getPath())
	log('Plugin: '+pName+' folder has been created')