import os
import subprocess
import pyautogui
import time
import socket
import struct
import atexit
import re
import random
import pyautogui
from twitchio.ext import commands
from dotenv import load_dotenv
import pyttsx3

engine = pyttsx3.init()
engine.setProperty('rate', 200)
def speak(text):
    print("saying in TTS: " + text)
    engine.say(text)
    engine.runAndWait()

# Load environment variables from chatgame.env
load_dotenv(dotenv_path='chatgame.env')

# Fetch OAuth token and channel from environment variables
oauth_token = os.getenv('TWITCH_OAUTH_TOKEN')
channel = os.getenv('TWITCH_USERNAME')
tts = os.getenv('TTS') != "f"
cell_inc = os.getenv('CELL_INC')
orb_inc = os.getenv('ORB_INC')
speed_inc = os.getenv('SPEED_INC')
jump_inc = os.getenv('JUMP_INC')
slip_res_inc = os.getenv('SLIP_RES_INC')
size_inc = os.getenv('SIZE_INC')
blue_eco_inc = os.getenv('BLUE_ECO_INC')
rolljump_inc = os.getenv('ROLLJUMP_INC')
boosted_inc = os.getenv('BOOSTED_INC')

mods = [channel, "mikegamepro"]

point_list = ["training-start","game-start","village1-hut","village1-warp","beach-start",
              "jungle-start","jungle-tower","misty-start","misty-silo","misty-bike",
              "misty-backside","misty-silo2","firecanyon-start","firecanyon-end",
              "village2-start","village2-warp","village2-dock","rolling-start",
              "sunken-start","sunken1","sunken2","sunken-tube1","sunkenb-start",
              "sunkenb-helix","swamp-start","swamp-dock1","swamp-cave1","swamp-dock2",
              "swamp-cave2","swamp-game","swamp-cave3","ogre-start","ogre-race","ogre-end",
              "village3-start","village3-warp","village3-farside","maincave-start",
              "maincave-to-darkcave","maincave-to-robocave","darkcave-start","robocave-start",
              "robocave-bottom","snow-start","snow-fort","snow-flut-flut","snow-pass-to-fort",
              "snow-by-ice-lake","snow-by-ice-lake-alt","snow-outside-fort","snow-outside-cave",
              "snow-across-from-flut","lavatube-start","lavatube-middle","lavatube-after-ribbon",
              "lavatube-end","citadel-start","citadel-entrance","citadel-warp","citadel-launch-start",
              "citadel-launch-end","citadel-generator-start","citadel-generator-end","citadel-plat-start",
              "citadel-plat-end","citadel-elevator","finalboss-start","finalboss-fight"]
death_list = ['melt', 'endlessfall', 'drown-death']

chat_test = False

class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=oauth_token, prefix='!', initial_channels=[channel])
        self.words_used = set()  # Store words that have already been used
        # Define effects and the words that trigger them
        self.effects = [
            {
                'name': 'Death',
                'theme': 'UNSC Vehicles',
                'command': lambda: f"(when (not (movie?))(target-attack-up *target* 'attack '{random.choice(death_list)}))",
                'triggers': ['warthog', 'mongoose', 'elephant', 'mammoth', 'scorpion', 'falcon', 'rhino', 'pelican', 'hornet']
            },
            {
                'name': 'Cell Increase',
                'theme': "People's Names",
                'command': f"(set! (-> *game-info* fuel)(max 0.0 (+ (-> *game-info* fuel) {cell_inc})))",
                'triggers': ['grant', 'may', 'will', 'chase', 'wade', 'joy', 'bill', 'summer', 'hunter', 'chance', 'clay']
            },
            {
                'name': 'Cell Decrease',
                'theme': 'Landmine Words',
                'command': f"(set! (-> *game-info* fuel)(max 0.0 (- (-> *game-info* fuel) {cell_inc})))",
                'triggers': ['whisper', 'spectrum', 'octopus', 'paradox', 'cloud', 'consume', 'splendid', 'twitch', 'elevator', 'squirrel', 'morning', 
                             'rocket', 'pillow', 'puzzle', 'sneeze', 'disaster', 'glove', 'mirrors', 'soda', 'revolution', 'ghost', 'prince', 'volcano', 
                             'robot', 'pencil', 'prawn', 'help', 'over', 'naughty', 'shake', 'spin', 'think', 'under', 'cope', 'strategy', 'lobster', 'chandelier', 
                             'archipelago', 'omega', 'cell', 'leave', 'crate', 'hospital', 'doctor', 'geologist', 'money', 'mine', 'secret', 'fart', 'homicide', 'cringe', 
                             'napkin', 'ban', 'run', 'chair', 'cat', 'rain', 'horse', 'chat', 'grandmother', 'gamble', 'hello' ,'spoiler', 'geyser', 'path', 'precursor', 
                             'cousin', 'niece', 'nephew', 'fly', 'battery', 'perfect', 'time', 'zoom', 'speed', 'industrial', 'outrageous', 'what', 'orbs', 'sorry', 'fire', 
                             'agriculture', 'laugh', 'dinner', 'breakfast', 'buffalo', 'crack', 'epic', 'happy', 'orange', 'indigo', 'bronze', 'homework', 'teacher', 'crime', 
                             'manslaughter', 'mercury', 'day', 'gamer', 'stellar']
            },
            {
                'name': 'Orb Increase',
                'theme': 'Underground Creatures',
                'command': f"(set! (-> *game-info* money)(max 0.0 (+ (-> *game-info* money) {orb_inc})))",
                'triggers': ['mole', 'earthworm', 'ant', 'badger', 'gopher', 'termite', 'groundhog']
            },
            {
                'name': 'Orb Decrease',
                'theme': 'Pizza Toppings',
                'command': f"(set! (-> *game-info* money)(max 0.0 (- (-> *game-info* money) {orb_inc})))",
                'triggers': ['pepperoni', 'pineapple', 'bacon', 'sausage', 'spinach']
            },
            {
                'name': 'Jump Height Boost',
                'theme': 'Minecraft Items',
                'command': f"(set! (-> *TARGET-bank* jump-height-max)(+ (-> *TARGET-bank* jump-height-max) (meters {jump_inc})))(set! (-> *TARGET-bank* double-jump-height-max)(+ (-> *TARGET-bank* double-jump-height-max) (meters {jump_inc})))",
                'triggers': ['furnace', 'bed', 'bucket', 'wool', 'coal', 'iron', 'obsidian']
            },
            {
                'name': 'Speed Boost',
                'theme': 'TV Shows',
                'command': f"(set! (-> *walk-mods* target-speed) (+ (-> *walk-mods* target-speed) (meters {speed_inc})))(set! (-> *double-jump-mods* target-speed) (+ (-> *double-jump-mods* target-speed) (meters {speed_inc})))(set! (-> *jump-mods* target-speed) (+ (-> *jump-mods* target-speed) (meters {speed_inc})))(set! (-> *jump-attack-mods* target-speed) (+ (-> *jump-attack-mods* target-speed) (meters {speed_inc})))(set! (-> *attack-mods* target-speed) (+ (-> *attack-mods* target-speed) (meters {speed_inc})))(set! (-> *forward-high-jump-mods* target-speed) (+ (-> *forward-high-jump-mods* target-speed) (meters {speed_inc})))(set! (-> *flip-jump-mods* target-speed) (+ (-> *flip-jump-mods* target-speed) (meters {speed_inc})))(set! (-> *high-jump-mods* target-speed) (+ (-> *high-jump-mods* target-speed) (meters {speed_inc})))(set! (-> *smack-jump-mods* target-speed) (+ (-> *smack-jump-mods* target-speed) (meters {speed_inc})))(set! (-> *duck-attack-mods* target-speed) (+ (-> *duck-attack-mods* target-speed) (meters {speed_inc})))(set! (-> *flop-mods* target-speed) (+ (-> *flop-mods* target-speed) (meters {speed_inc})))",
                'triggers': ['glee', 'friends', 'arrow', 'scrubs', 'survivor', 'lost', 'cheers']
            },
            {
                'name': 'Blue Eco',
                'theme': 'Pokémon Games',
                'command': "(send-event *target* 'get-pickup (pickup-type eco-blue) 5.0)",
                'triggers': ['blue', 'silver', 'crystal', 'emerald', 'sapphire', 'diamond', 'platinum', 'white', 'moon', 'sword', 'violet']
            },
            {
                'name': 'Red Eco',
                'theme': 'Animal Groups',
                'command': "(send-event *target* 'get-pickup (pickup-type eco-red) 5.0)",
                'triggers': ['murder', 'parliament', 'gaggle', 'school', 'drove', 'pride', 'flock', 'pack']
            },
            {
                'name': 'Yellow Eco',
                'theme': 'Things Before "Day"',
                'command': "(send-event *target* 'get-pickup (pickup-type eco-yellow) 5.0)",
                'triggers': ['laundry', 'green', 'memorial', 'pay', 'birth', 'independence', 'sick', 'sun']
            },
            {
                'name': 'Trip',
                'theme': 'Palindromes',
                'command': "(send-event *target* 'loading)",
                'triggers': ['noon', 'kayak', 'radar', 'racecar', 'refer', 'level', 'civic', 'deified', 'tenet', 'madam', 'rotor']
            },
            {
                'name': 'Invulnerability',
                'theme': 'Types of Piles',
                'command': "(set! (-> *pc-settings* speedrunner-mode?) #f)(begin (logior! (-> *pc-settings* cheats) (pc-cheats invinc)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats invinc)))",
                'command2': "(logclear! (-> *pc-settings* cheats) (pc-cheats invinc))(logclear! (-> *target* state-flags) (state-flags invulnerable))",
                'triggers': ['snow', 'dog', 'dirt', 'leaf', 'trash'],
                'toggle': False
            },
            {
                'name': 'Rapid Fire',
                'theme': 'Wildcard 1',
                'command': "(set! (-> *TARGET-bank* yellow-projectile-speed) (meters 100))(set! (-> *TARGET-bank* yellow-attack-timeout) (seconds 0))",
                'triggers': ['bumble']
            },
            {
                'name': 'Damage',
                'theme': 'Movie Genres',
                'command': "(if (not (= *target* #f))(target-attack-up *target* 'attack 'burnup))",
                'triggers': ['action', 'comedy', 'drama', 'horror', 'thriller', 'romantic', 'adventure', 'mystery', 'fantasy', 'documentary', 'musical', 'western']
            },
            {
                'name': 'Slip Resistance"',
                'theme': 'Synonyms of "Ridiculous"',
                'command': f"(set! (-> *pat-mode-info* 1 wall-angle) (max 0.0 (- (-> *pat-mode-info* 1 wall-angle) {float(slip_res_inc)})))(set! (-> *pat-mode-info* 2 wall-angle) (max 0.0 (- (-> *pat-mode-info* 2 wall-angle) {float(slip_res_inc) / 2.44})))",
                'triggers': ['absurd', 'preposterous', 'ludicrous', 'outlandish']
            },
            {
                'name': 'Mirror World',
                'theme': 'Carnival',
                'command': "(set! (-> *pc-settings* speedrunner-mode?) #f)(begin (logior! (-> *pc-settings* cheats) (pc-cheats mirror)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats mirror)))",
                'command2': "(logclear! (-> *pc-settings* cheats) (pc-cheats mirror))",
                'triggers': ['cotton', 'carousel', 'paint', 'acrobat'],
                'toggle': False
            },
            #{
            #    'name': 'Size Increase',
            #    'theme': 'none',
            #    'command': f"(set! (-> (-> (the-as target *target* )root)scale x) (+ (-> (-> (the-as target *target* )root)scale x) {size_inc}))(set! (-> (-> (the-as target *target* )root)scale y) (+ (-> (-> (the-as target *target* )root)scale y) {size_inc}))(set! (-> (-> (the-as target *target* )root)scale z) (+ (-> (-> (the-as target *target* )root)scale z) {size_inc}))",
            #    'triggers': ['mm', 'nn', 'oo', 'pp'],
            #},
            #{
            #    'name': 'Size Decrease',
            #    'theme': 'none',
            #    'command': f"(set! (-> (-> (the-as target *target* )root)scale x) (- (-> (-> (the-as target *target* )root)scale x) {size_inc}))(set! (-> (-> (the-as target *target* )root)scale y) (- (-> (-> (the-as target *target* )root)scale y) {size_inc}))(set! (-> (-> (the-as target *target* )root)scale z) (- (-> (-> (the-as target *target* )root)scale z) {size_inc}))",
            #    'triggers': ['qq', 'rr', 'ss', 'tt'],
            #},
            {
                'name': 'Inverted Camera',
                'theme': 'Gardening Tasks',
                'command': f"(set! (-> *pc-settings* third-camera-h-inverted?) (not (-> *pc-settings* third-camera-h-inverted?)))",
                'triggers': ['harvest', 'mulch', 'compost', 'weed', 'water', 'plant'],
            },
            {
                'name': 'Random Checkpoint',
                'theme': 'Many Meanings',
                'command': lambda: f"(start 'play (get-continue-by-name *game-info* \"{point_list[random.choice(range(0,52))]}\"))(auto-save-command 'auto-save 0 0 *default-pool*)",
                'triggers': ['well', 'bat', 'lead', 'light', 'spring', 'match', 'date', 'bowl', 'seal'],
            },
            {
                'name': 'Blue Eco Range Increase',
                'theme': 'Musical Terms',
                'command': f"(set! (-> *FACT-bank* suck-suck-dist) (max (meters 1.5) (+ (-> *FACT-bank* suck-suck-dist) (meters {blue_eco_inc}))))(set! (-> *FACT-bank* suck-bounce-dist) (max (meters 2) (+ (-> *FACT-bank* suck-bounce-dist) (meters {blue_eco_inc}))))",
                'triggers': ['vibrato', 'chord', 'sonata', 'harmony', 'arpeggio', 'cadence', 'melody', 'scale', 'key', 'tempo', 'chorus'],
            },
            {
                'name': 'Blue Eco Range Decrease',
                'theme': 'Things That Are Purple',
                'command': f"(set! (-> *FACT-bank* suck-suck-dist) (max (meters 1.5) (- (-> *FACT-bank* suck-suck-dist) (meters {blue_eco_inc}))))(set! (-> *FACT-bank* suck-bounce-dist) (max (meters 2) (- (-> *FACT-bank* suck-bounce-dist) (meters {blue_eco_inc}))))",
                'triggers': ['grimace', 'eggplant', 'lavender', 'amethyst'],
            },
            {
                'name': 'Slippery Ground',
                'theme': 'Sound Like Letters',
                'command': "(set! (-> *stone-surface* slip-factor) 0.7)(set! (-> *stone-surface* transv-max) 1.5)(set! (-> *stone-surface* turnv) 0.5)(set! (-> *stone-surface* nonlin-fric-dist) 4091904.0)(set! (-> *stone-surface* fric) 23756.8)(set! (-> *grass-surface* slip-factor) 0.7)(set! (-> *grass-surface* transv-max) 1.5)(set! (-> *grass-surface* turnv) 0.5)(set! (-> *grass-surface* nonlin-fric-dist) 4091904.0)(set! (-> *grass-surface* fric) 23756.8)(set! (-> *ice-surface* slip-factor) 0.3)(set! (-> *ice-surface* nonlin-fric-dist) 8183808.0)(set! (-> *ice-surface* fric) 11878.4)",
                'command2': "(set! (-> *stone-surface* slip-factor) 1.0)(set! (-> *stone-surface* transv-max) 1.0)(set! (-> *stone-surface* turnv) 1.0)(set! (-> *stone-surface* nonlin-fric-dist) 5120.0)(set! (-> *stone-surface* fric) 153600.0)(set! (-> *grass-surface* slip-factor) 1.0)(set! (-> *grass-surface* transv-max) 1.0)(set! (-> *grass-surface* turnv) 1.0)(set! (-> *grass-surface* nonlin-fric-dist) 4096.0)(set! (-> *grass-surface* fric) 122880.0)(set! (-> *ice-surface* slip-factor) 0.7)(set! (-> *ice-surface* nonlin-fric-dist) 4091904.0)(set! (-> *ice-surface* fric) 23756.8)",
                'triggers': ['bee', 'sea', 'eye', 'you', 'tea', 'are'],
                'toggle': False
            },
            {
                'name': 'No Ledge Grabs',
                'theme': 'Nonviolent Crimes',
                'command': "(set! (-> *collide-edge-work* max-dir-cosa-delta) 999.0)",
                'command2': "(set! (-> *collide-edge-work* max-dir-cosa-delta) 0.6)",
                'triggers': ['fraud', 'embezzlement', 'possession', 'forgery'],
                'toggle': False
            },
            {
                'name': 'Deload Level',
                'theme': 'Immediate Relatives',
                'command': "(when (not (movie?))(set! (-> *load-state* want 0 display?) #f))",
                'triggers': ['brother', 'daughter', 'father', 'sister', 'mother', 'son'],
            },
            {
                'name': 'Rolljump Increase',
                'theme': 'College Majors',
                'command': f"(set! (-> *TARGET-bank* wheel-flip-dist) (+ (meters {rolljump_inc}) (-> *TARGET-bank* wheel-flip-dist)))",
                'triggers': ['psychology', 'biology', 'engineering', 'nursing', 'history', 'english', 'economics', 'education'],
            },
            {
                'name': 'Rolljump Decrease',
                'theme': 'Found on a Beach',
                'command': f"(set! (-> *TARGET-bank* wheel-flip-dist) (- (-> *TARGET-bank* wheel-flip-dist) (meters {rolljump_inc})))",
                'triggers': ['wave', 'towel', 'shell', 'cooler', 'umbrella'],
            },
            {
                'name': 'No Textures',
                'theme': 'Like U.S. State Names',
                'command': "(set! (-> *pc-settings* speedrunner-mode?) #f)(begin (logior! (-> *pc-settings* cheats) (pc-cheats no-tex)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats no-tex)))",
                'command2': "(logclear! (-> *pc-settings* cheats) (pc-cheats no-tex))",
                'triggers': ['road', 'misery', 'origin', 'connect'],
                'toggle': False
            },
            {
                'name': 'Big Head NPCs',
                'theme': 'Last Word of Jak 1 Levels',
                'command': "(set! (-> *pc-settings* speedrunner-mode?) #f)(begin (logior! (-> *pc-settings* cheats) (pc-cheats big-head-npc)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats big-head-npc)))",
                'command2': "(logclear! (-> *pc-settings* cheats) (pc-cheats big-head-npc))",
                'triggers': ['rock', 'village', 'island', 'city', 'basin', 'swamp', 'crater', 'citadel', 'tube', 'jungle', 'canyon', 'beach', 'cave', 'mountain', 'pass'],
                'toggle': False
            },
            {
                'name': 'Decrease Boosted Distance',
                'theme': 'Types of Clocks',
                'command': f"(set! (-> *edge-surface* fric) (+ {float(boosted_inc)} (-> *edge-surface* fric)))",
                'triggers': ['grandfather', 'cuckoo', 'alarm'],
            },
            {
                'name': 'Low Poly',
                'theme': 'Bands Without The Number',
                'command': "(set! (-> *pc-settings* lod-force-tfrag) 2)(set! (-> *pc-settings* lod-force-tie) 3)(set! (-> *pc-settings* lod-force-ocean) 2)(set! (-> *pc-settings* lod-force-actor) 3)",
                'command2': "(set! (-> *pc-settings* lod-force-tfrag) 0)(set! (-> *pc-settings* lod-force-tie) 0)(set! (-> *pc-settings* lod-force-ocean) 0)(set! (-> *pc-settings* lod-force-actor) 0)",
                'triggers': ['blink', 'sum', 'republic', 'pilots', 'maroon', 'eve'],
                'toggle': False
            },
            {
                'name': 'Increase Boosted Distance',
                'theme': 'Math Results',
                'command': f"(set! (-> *edge-surface* fric) (- (-> *edge-surface* fric) {float(boosted_inc)}))",
                'triggers': ['product', 'remainder', 'difference', 'quotient', 'power'],
            },
            {
                'name': 'No Effect 1',
                'theme': 'Start and End With "T"',
                'command': "",
                'triggers': ['tarot', 'trident', 'tract', 'talent', 'test', 'treat', 'trust', 'thought'],
            },
            {
                'name': 'poop',
                'theme': 'poop',
                'command': "",
                'triggers': ['poop'],
            },
            {
                'name': 'Back 2 Geyser',
                'theme': 'Wildcard 2',
                'command': "(start 'play (get-continue-by-name *game-info* \"intro-start\"))(auto-save-command 'auto-save 0 0 *default-pool*)",
                'triggers': ['ingredient'],
            },
            {
                'name': 'Cell Bundle 1',
                'theme': 'Wildcard 3',
                'command': "(set! (-> *game-info* fuel)(max 0.0 (+ (-> *game-info* fuel) 2)))",
                'triggers': ['rainbow'],
            },
            {
                'name': 'Cell Bundle 2',
                'theme': 'Wildcard 4',
                'command': "(set! (-> *game-info* fuel)(max 0.0 (+ (-> *game-info* fuel) 2)))",
                'triggers': ['galaxy'],
            },
            {
                'name': 'Cell Bundle 3',
                'theme': 'Wildcard 5',
                'command': "(set! (-> *game-info* fuel)(max 0.0 (+ (-> *game-info* fuel) 2)))",
                'triggers': ['marble'],
            },
        ]
        self.effects_found = {}
        self.goalc_process = None
        self.clientSocket = None

        atexit.register(self.cleanup)

    def cleanup(self):
        if self.clientSocket:
            self.clientSocket.close()
            print("Closed client socket.")
        if self.goalc_process:
            self.goalc_process.terminate()
            print("Terminated goalc process.")
        if self.gk_process:
            self.gk_process.terminate()
            print("Terminated gk process.")
        print("Cleaned up resources.")

    # Event: When the bot connects to Twitch chat
    async def event_ready(self):
        print(f'Logged in as | {channel}')
        print(f'Connected to channel | {self.connected_channels}')
        # Start goalc.exe when bot is ready
        self.launch_game()

    # This function handles chat messages and specific commands
    async def event_message(self, message):
        # Ignore messages from the bot itself, unless they are commands
        if (message.author.name.lower() == channel.lower() and not chat_test) and not message.content.startswith('!'):
            return  # Ignore other messages from the bot itself

        chat_message = message.content.lower().strip()
        print(f"Received message: {chat_message}")

        # Check for start and stop commands
        if chat_message == "!startgame" and message.author.name.lower() in mods:
            self.active = True
            await self.send_message(channel, "Word processing started!")
            return
        elif chat_message == "!stopgame" and message.author.name.lower() in mods:
            self.active = False
            await self.send_message(channel, "Word processing stopped!")
            return

        # Process custom command for showing found words for an effect
        if chat_message.startswith('!'):
            await self.handle_custom_commands(chat_message, message.author.name)
            return

        # Only process messages if active
        if self.active:
            user = message.author.name
            await self.handle_chat_message(chat_message, user)

    async def handle_chat_message(self, chat_message, user):
        for effect in self.effects:
            for word in effect['triggers']:
                if re.search(r'\b' + re.escape(word) + r'\b', chat_message) and word not in self.words_used:
                    await self.trigger_effect(effect, word, user)
                    self.words_used.add(word)
                    self.effects_found[effect['name']] = self.effects_found.get(effect['name'], []) + [word]
                    remaining_words = set(effect['triggers']) - self.words_used
                    await self.send_message(channel, f"{user} found {effect['name']} with '{word}' ({len(effect['triggers']) - len(remaining_words)}/{len(effect['triggers'])})!")
                    if tts: 
                        speak(f"{user} found {effect['name']} with '{word}'")
                    break

            if all(w in self.effects_found.get(effect['name'], []) for w in effect['triggers']):
                await self.send_message(channel, f"All words found for {effect['name']} ({effect['theme']})!")
                self.send_form(f"(set! (-> *game-info* fuel)(max 0.0 (+ (-> *game-info* fuel) {cell_inc})))")
                if tts:
                    speak(f"All words found for {effect['name']} -- ({effect['theme']})!")
                self.effects_found[effect['name']] = []  # Reset for the next round

    # Handle chat commands, including requests for showing found words for an effect
    async def handle_custom_commands(self, command, user):
        command = command.strip().lower()
        
        # Check if the command corresponds to any effect
        for effect in self.effects:
            effect_command = "!"+effect['name'].replace(" ", "").lower()  # Make a clean command (e.g., "!speedboost")
            
            if command == effect_command:
                # Gather all found words for the effect
                found_words = self.effects_found.get(effect['name'], [])
                
                # If no words have been found, notify the user
                if not found_words:
                    #await self.send_message(channel, f"{effect['name']} has no words found yet.")
                    return
                else:
                    # Show all found words
                    found_words_str = ", ".join(found_words)
                    await self.send_message(channel, f"{effect['name']}: {found_words_str}")
                return  # Exit the loop after handling the correct command

    async def trigger_effect(self, effect, word, user):
        if 'toggle' in effect and effect['toggle']:
            effect['toggle'] = False
            command_to_send = effect['command2']
        else:
            if callable(effect['command']):
                command_to_send = effect['command']()
            else:
                command_to_send = effect['command']
            if 'toggle' in effect:
                effect['toggle'] = True

        self.send_form(command_to_send)

    async def send_message(self, channel, message):
        """Send a message to the channel."""
        await self.get_channel(channel).send(f"-> {message}")
    
    def launch_game(self):
        try:
            # Start gk.exe first
            self.gk_process = subprocess.Popen(['gk.exe', '-v', '--', '-boot', '-fakeiso', '-debug'], cwd=os.getcwd())
            
            # Wait for a moment to ensure gk.exe initializes properly
            time.sleep(2)
            
            # Start goalc.exe
            self.goalc_process = subprocess.Popen(['goalc.exe'], cwd=os.getcwd())
            
            # Optionally, wait for the goalc process to initialize
            time.sleep(2)

            # Set up the socket connection to goalc.exe here if necessary
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clientSocket.connect(("127.0.0.1", 8181))

            # Receive initial data (if applicable)
            data = self.clientSocket.recv(1024)
            print(data.decode())

            self.send_form('(lt)')
            self.send_form('(mi)')
        except Exception as e:
            print(f"Error launching gk or goalc: {e}")

    def send_form(self, form):
        header = struct.pack('<II', len(form), 10)
        self.clientSocket.sendall(header + form.encode())
        print("Sent: " + form)

# Initialize and run the bot
bot = TwitchBot()
bot.run()