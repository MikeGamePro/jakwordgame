import os
import subprocess
import pyautogui
import time
import socket
import struct
import atexit
import re
import random
import pyttsx3
from twitchio.ext import commands
from dotenv import load_dotenv
import asyncio
import sys
import json

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 200)
def speak(text):
    if tts:
        print("saying in TTS: " + text)
        engine.say(text)
        engine.runAndWait()

# Load environment variables from chatgame.env
load_dotenv(dotenv_path='chatgame.env')

# Fetch environment variables with default values
oauth_token = os.getenv('TWITCH_OAUTH_TOKEN')
channel = os.getenv('TWITCH_USERNAME')
tts = os.getenv('TTS', 't').lower() != "f"
min_cell_count = float(os.getenv('MIN_CELL_COUNT', -10))
cell_inc = int(os.getenv('CELL_INC', 1))
cell_bundle = int(os.getenv('CELL_BUNDLE', 2))
cell_drain = int(os.getenv('CELL_DRAIN', 4))
orb_inc = int(os.getenv('ORB_INC', 90))
speed_inc = float(os.getenv('SPEED_INC', 2.2))
jump_inc = float(os.getenv('JUMP_INC', 1.0))
slip_res_inc = float(os.getenv('SLIP_RES_INC', 0.5))
size_inc = float(os.getenv('SIZE_INC', 0.15))
blue_eco_inc = float(os.getenv('BLUE_ECO_INC', 5.0))
rolljump_inc = float(os.getenv('ROLLJUMP_INC', 2.0))
boosted_inc = float(os.getenv('BOOSTED_INC', 8500.0))
iframes_inc = float(os.getenv('IFRAMES_INC', 1.0))
spin_inc = float(os.getenv('SPIN_INC', 1.0))
grav_mul = float(os.getenv('GRAVITY_MUL', 1.2))

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
boom_list = ['dcrate-break', 'explosion', 'explosion-2', 'zoomer-explode', 'blob-explode']

chat_test = False

class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=oauth_token, prefix='!', initial_channels=[channel])
        self.words_used = set()
        # Define effects and the words that trigger them
        self.effects = [
                    {
                        'name': 'Death',
                        'theme': 'Twitch',
                        'command': lambda: f"(when (not (movie?))(target-attack-up *target* 'attack '{random.choice(death_list)}))",
                        'triggers': [['bit', 'bits'], 'chat', 'stream', 'subscribe', 'buffer', 'raid', 'follow', 'amazon', 'live', 'channel']
                    },
                    {
                        'name': 'Cell Increase',
                        'theme': "The 'G' is Silent",
                        'command': f"(set! (-> *game-info* fuel)(max {min_cell_count} (+ (-> *game-info* fuel) {cell_inc})))",
                        'triggers': ['weigh', 'sleigh', 'champagne', 'design', 'gnat', 'gnaw', 'gnome', 'sign', 'align', 'reign', 'light', 'though', 'sigh', 'benign', 'foreign', 'campaign', 'resign']
                    },
                    {
                        'name': 'Cell Decrease',
                        'theme': 'Landmine Words',
                        'command': f"(set! (-> *game-info* fuel)(max {min_cell_count} (- (-> *game-info* fuel) {cell_inc})))",
                        'triggers': ['little', 'sting', 'sketch', 'debate', 'luggage', 'envelope', 'magnet', 'circus', 'calculator', 'quantum', 
                                     'helicopter', 'paradox', 'ink', 'bell', 'glove', 'hypothesis', 'chair', 'infinity', 'random', 'rhombus', 'science', 'flute', 
                                     'thank', 'radio', 'scrub', 'giraffe', 'trampoline', 'canyon', 'combat', 'statue', 'monopoly', 'dinosaur', 'ruler', 'helmet', 
                                     'omega', 'library', 'spectrum', 'mushroom', 'clown', 'universe', 'matrix', 'chemistry', 'equation', 'compass', 'fog', 'recipe', 'ingredient', 
                                     'alarm', 'cake', 'angry', 'glacier', 'active', 'velvet', 'potion', 'podium', 'landmine', 'hello' ,'spoon', 'puddle', 'violin', 'portrait', 
                                     'quick', 'lantern', 'opposite', 'mad', 'zero', 'last', 'third', 'tomb', 'speed', 'industrial', 'outrage', 'what', 'prawn', 
                                     'agriculture', 'flock', 'mango', 'pigeon', 'project', 'crack', 'first', 'happy', 'yellow', 'confused', 'bronze', 'work', 
                                     'teacher', 'manslaughter', 'mercury', 'ray', 'gamer', 'general', 'scatter', 'visit', 'fresh', 'phosphate', 'electric', 'bound', 
                                     'weiner', 'suffer', 'supercalifragilisticexpialidocious']
                    },
                    {
                        'name': 'Orb Increase',
                        'theme': 'Pirate',
                        'command': f"(set! (-> *game-info* money)(max -90.0 (+ (-> *game-info* money) {orb_inc})))",
                        'triggers': ['plank', 'peg', 'cannon', 'parrot', 'rum', 'captain', 'treasure', 'hook']
                    },
                    {
                        'name': 'Orb Decrease',
                        'theme': 'Periods of Time',
                        'command': f"(set! (-> *game-info* money)(max -90.0 (- (-> *game-info* money) {orb_inc})))",
                        'triggers': ['century', 'fortnight', 'year', 'day', 'month', 'second', 'eon', 'hour']
                    },
                    {
                        'name': 'Jump Boost',
                        'theme': 'Windows Commands',
                        'command': f"(set! (-> *TARGET-bank* jump-height-max)(+ (-> *TARGET-bank* jump-height-max) (meters {jump_inc})))(set! (-> *TARGET-bank* double-jump-height-max)(+ (-> *TARGET-bank* double-jump-height-max) (meters {jump_inc})))",
                        'triggers': ['cut', 'paste', 'undo', 'print', 'find', 'copy', 'save']
                    },
                    {
                        'name': 'Speed Boost',
                        'theme': 'Elements of Art',
                        'command': f"(set! (-> *walk-mods* target-speed) (+ (-> *walk-mods* target-speed) (meters {speed_inc})))(set! (-> *double-jump-mods* target-speed) (+ (-> *double-jump-mods* target-speed) (meters {speed_inc})))(set! (-> *jump-mods* target-speed) (+ (-> *jump-mods* target-speed) (meters {speed_inc})))(set! (-> *jump-attack-mods* target-speed) (+ (-> *jump-attack-mods* target-speed) (meters {speed_inc})))(set! (-> *attack-mods* target-speed) (+ (-> *attack-mods* target-speed) (meters {speed_inc})))(set! (-> *forward-high-jump-mods* target-speed) (+ (-> *forward-high-jump-mods* target-speed) (meters {speed_inc})))(set! (-> *flip-jump-mods* target-speed) (+ (-> *flip-jump-mods* target-speed) (meters {speed_inc})))(set! (-> *high-jump-mods* target-speed) (+ (-> *high-jump-mods* target-speed) (meters {speed_inc})))(set! (-> *smack-jump-mods* target-speed) (+ (-> *smack-jump-mods* target-speed) (meters {speed_inc})))(set! (-> *duck-attack-mods* target-speed) (+ (-> *duck-attack-mods* target-speed) (meters {speed_inc})))(set! (-> *flop-mods* target-speed) (+ (-> *flop-mods* target-speed) (meters {speed_inc})))",
                        'triggers': ['line', 'shape', 'texture', 'form', 'space', 'value', ['color', 'colour']]
                    },
                    {
                        'name': 'No Punch or Spin',
                        'theme': 'Things That Come Back',
                        'command': "(set! (-> *TARGET-bank* attack-timeout)(seconds 999999))",
                        'command2': "(set! (-> *TARGET-bank* attack-timeout)(seconds 0.3))",
                        'triggers': ['echo', 'reflection', 'boomerang', 'karma'],
                        'toggle': False
                    },
                    {
                        'name': 'Blue Eco',
                        'theme': 'Counter-Strike Maps',
                        'command': "(send-event *target* 'get-pickup (pickup-type eco-blue) 5.0)",
                        'triggers': ['dust', 'inferno', 'mirage', 'nuke', 'train', 'office', 'cache', 'overpass', 'cobblestone', 'ancient', 'vertigo']
                    },
                    {
                        'name': 'Red Eco',
                        'theme': 'Start of U.S. State Names',
                        'command': "(send-event *target* 'get-pickup (pickup-type eco-red) 5.0)",
                        'triggers': ['wash', 'miss', 'ten', 'pen', 'main', 'ill', 'ark', 'color', 'mass', 'ore', 'alas']
                    },
                    {
                        'name': 'Yellow Eco',
                        'theme': 'After "Great"',
                        'command': "(send-event *target* 'get-pickup (pickup-type eco-yellow) 5.0)",
                        'triggers': [['expectations', 'expectation'], ['pyramid', 'pyramids'], 'escape', 'depression', ['lake', 'lakes'], 'plains', 'wall']
                    },
                    {
                        'name': 'Trip',
                        'theme': 'Disney Films',
                        'command': "(send-event *target* 'loading)",
                        'triggers': ['pan', 'snow', 'lion', 'tangled', 'frozen', 'lady', 'beauty', 'mermaid', 'fantasia', 'stitch', 'jungle']
                    },
                    {
                        'name': 'BOOM',
                        'theme': 'Jak 3 Locations',
                        'command': lambda: f"(sound-play \"{random.choice(boom_list)}\")",
                        'triggers': ['nest', 'ship', ['mine', 'mines'], 'haven', 'volcano', 'oasis', 'port', 'course', 'temple', ['sewers', 'sewer'], 'factory', 'palace']
                    },
                    {
                        'name': 'Invulnerability',
                        'theme': 'Story Elements',
                        'command': "(begin (logior! (-> *pc-settings* cheats) (pc-cheats invinc)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats invinc)))",
                        'command2': "(logclear! (-> *pc-settings* cheats) (pc-cheats invinc))(logclear! (-> *target* state-flags) (state-flags invulnerable))",
                        'triggers': ['character', 'setting', 'plot', 'conflict', 'climax' 'resolution'],
                        'toggle': False
                    },
                    {
                        'name': 'Damage',
                        'theme': 'Jak Runners',
                        'command': "(if (not (= *target* #f))(target-attack-up *target* 'attack 'burnup))",
                        'triggers': ['bin', 'vortex', 'stellar', 'headstrong', 'flu', 'bob', 'wed', 'goofy', 'jazz', 'usual', 'six', 'scar', 'blue', 'boomer', 'zed']
                    },
                    {
                        'name': 'Slip Resistance',
                        'theme': 'Types of Sauces',
                        'command': f"(set! (-> *pat-mode-info* 1 wall-angle) (max 0.0 (- (-> *pat-mode-info* 1 wall-angle) {slip_res_inc})))(set! (-> *pat-mode-info* 2 wall-angle) (max 0.0 (- (-> *pat-mode-info* 2 wall-angle) {slip_res_inc / 2.44})))",
                        'triggers': ['hot', 'cocktail', 'tomato', 'chocolate']
                    },
                    {
                        'name': 'I-Frames Increase',
                        'theme': 'Baseball Terms',
                        'command': f"(set! (-> *TARGET-bank* hit-invulnerable-timeout) (+ (-> *TARGET-bank* hit-invulnerable-timeout) (seconds {iframes_inc})))",
                        'triggers': ['base', 'field', 'bunt', 'pitch', 'mound', 'strike']
                    },
                    {
                        'name': 'I-Frames Decrease',
                        'theme': 'After "Foot"',
                        'command': f"(set! (-> *TARGET-bank* hit-invulnerable-timeout) (- (-> *TARGET-bank* hit-invulnerable-timeout) (seconds {iframes_inc})))",
                        'triggers': ['loose', 'print', 'step']
                    },
                    {
                        'name': 'Mirror World',
                        'theme': 'Found in a Construction Site',
                        'command': "(begin (logior! (-> *pc-settings* cheats) (pc-cheats mirror)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats mirror)))",
                        'command2': "(logclear! (-> *pc-settings* cheats) (pc-cheats mirror))",
                        'triggers': ['crane', 'cement', 'hammer', 'beam'],
                        'toggle': False
                    },
                    {
                        'name': 'Inverted Camera',
                        'theme': 'Prison',
                        'command': f"(set! (-> *pc-settings* third-camera-h-inverted?) (not (-> *pc-settings* third-camera-h-inverted?)))",
                        'triggers': ['cell', 'warden', 'convict', 'guard', 'sentence', 'bail'],
                    },
                    {
                        'name': 'Random Checkpoint',
                        'theme': 'Ways to Say "Eat"',
                        'command': lambda: f"(start 'play (get-continue-by-name *game-info* \"{point_list[random.choice(range(0,52))]}\"))(auto-save-command 'auto-save 0 0 *default-pool*)",
                        'triggers': ['consume', 'devour', 'ingest', 'feast', 'scarf', 'gorge', 'partake', 'dine'],
                    },
                    {
                        'name': 'Blue Eco Range Increase',
                        'theme': 'Things You Take',
                        'command': f"(set! (-> *FACT-bank* suck-suck-dist) (max (meters 1.5) (+ (-> *FACT-bank* suck-suck-dist) (meters {blue_eco_inc}))))(set! (-> *FACT-bank* suck-bounce-dist) (max (meters 2) (+ (-> *FACT-bank* suck-bounce-dist) (meters {blue_eco_inc}))))",
                        'triggers': ['break', 'chance', 'look', 'bite', 'seat', 'stand', 'breath', 'hike', 'risk', 'nap', 'bath', 'hint'],
                    },
                    {
                        'name': 'Blue Eco Range Decrease',
                        'theme': 'Things That Spin',
                        'command': f"(set! (-> *FACT-bank* suck-suck-dist) (max (meters 1.5) (- (-> *FACT-bank* suck-suck-dist) (meters {blue_eco_inc}))))(set! (-> *FACT-bank* suck-bounce-dist) (max (meters 2) (- (-> *FACT-bank* suck-bounce-dist) (meters {blue_eco_inc}))))",
                        'triggers': ['globe', 'top', 'wheel', 'fan'],
                    },
                    {
                        'name': 'Slippery Ground',
                        'theme': "Doctor's Office",
                        'command': "(set! (-> *stone-surface* slip-factor) 0.8)(set! (-> *stone-surface* transv-max) 1.3)(set! (-> *stone-surface* turnv) 0.56)(set! (-> *stone-surface* nonlin-fric-dist) 3600875.0)(set! (-> *stone-surface* fric) 23756.8)(set! (-> *grass-surface* slip-factor) 0.8)(set! (-> *grass-surface* transv-max) 1.3)(set! (-> *grass-surface* turnv) 0.56)(set! (-> *grass-surface* nonlin-fric-dist) 3600875.0)(set! (-> *grass-surface* fric) 26726.4)(set! (-> *ice-surface* slip-factor) 0.33)(set! (-> *ice-surface* nonlin-fric-dist) 7201750.0)(set! (-> *ice-surface* fric) 13363.4)",
                        'command2': "(set! (-> *stone-surface* slip-factor) 1.0)(set! (-> *stone-surface* transv-max) 1.0)(set! (-> *stone-surface* turnv) 1.0)(set! (-> *stone-surface* nonlin-fric-dist) 5120.0)(set! (-> *stone-surface* fric) 153600.0)(set! (-> *grass-surface* slip-factor) 1.0)(set! (-> *grass-surface* transv-max) 1.0)(set! (-> *grass-surface* turnv) 1.0)(set! (-> *grass-surface* nonlin-fric-dist) 4096.0)(set! (-> *grass-surface* fric) 122880.0)(set! (-> *ice-surface* slip-factor) 0.7)(set! (-> *ice-surface* nonlin-fric-dist) 4091904.0)(set! (-> *ice-surface* fric) 23756.8)",
                        'triggers': ['prescription', 'exam', 'nurse', 'diagnosis', 'appointment', 'bandage', 'referral', 'vaccine'],
                        'toggle': False
                    },
                    {
                        'name': 'No Ledge Grabs',
                        'theme': 'Game Environments',
                        'command': "(set! (-> *collide-edge-work* max-dir-cosa-delta) 999.0)",
                        'command2': "(set! (-> *collide-edge-work* max-dir-cosa-delta) 0.6)",
                        'triggers': ['stage', 'level', 'world', 'zone'],
                        'toggle': False
                    },
                    {
                        'name': 'Deload Level',
                        'theme': 'NATO Phonetic Alphabet',
                        'command': "(when (not (movie?))(set! (-> *load-state* want 0 display?) #f)(set! (-> *load-state* want 1 display?) #f))",
                        'triggers': ['golf', 'november', 'victor', 'whiskey', 'hotel', 'uniform'],
                    },
                    {
                        'name': 'Rolljump Increase',
                        'theme': 'Units of Measurement',
                        'command': f"(set! (-> *TARGET-bank* wheel-flip-dist) (+ (meters {rolljump_inc}) (-> *TARGET-bank* wheel-flip-dist)))",
                        'triggers': ['pressure', 'force', 'speed', 'temperature', 'area', 'volume', 'weight', 'distance'],
                    },
                    {
                        'name': 'Rolljump Decrease',
                        'theme': 'Common Pet Names',
                        'command': f"(set! (-> *TARGET-bank* wheel-flip-dist) (- (-> *TARGET-bank* wheel-flip-dist) (meters {rolljump_inc})))",
                        'triggers': ['buddy', 'lucky', 'mittens', 'fluffy', 'biscuit'],
                    },
                    {
                        'name': 'No Textures',
                        'theme': 'Types of Bears',
                        'command': "(begin (logior! (-> *pc-settings* cheats) (pc-cheats no-tex)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats no-tex)))",
                        'command2': "(logclear! (-> *pc-settings* cheats) (pc-cheats no-tex))",
                        'triggers': ['grizzly', 'black', 'brown', 'gummy', 'panda', 'polar'],
                        'toggle': False
                    },
                    {
                        'name': 'Big Head NPCs',
                        'theme': 'Homophones',
                        'command': "(begin (logior! (-> *pc-settings* cheats) (pc-cheats big-head-npc)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats big-head-npc)))",
                        'command2': "(logclear! (-> *pc-settings* cheats) (pc-cheats big-head-npc))",
                        'triggers': ['bare', 'flour', 'higher', 'write', 'peace', 'blew', 'knight', 'weak', 'allowed', 'stair', 'reign', 'eight', 'board', 'cereal', 'knot', "manor", "suite"],
                        'toggle': False
                    },
                    {
                        'name': 'Head Size',
                        'theme': 'Game Shows',
                        'command': lambda: random.choice(["(begin (logior! (-> *pc-settings* cheats) (pc-cheats big-head)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats big-head)))",
                                            "(begin (logior! (-> *pc-settings* cheats) (pc-cheats small-head)) (logclear! (-> *pc-settings* cheats-known) (pc-cheats small-head)))"]),
                        'command2': "(logclear! (-> *pc-settings* cheats) (pc-cheats small-head))(logclear! (-> *pc-settings* cheats) (pc-cheats big-head))",
                        'triggers': ['feud', 'jeopardy', 'fortune', 'millionaire', 'price', 'deal', 'password', 'match'],
                        'toggle': False
                    },
                    {
                        'name': 'Boosted Decrease',
                        'theme': 'Methods of Unlocking',
                        'command': f"(set! (-> *edge-surface* fric) (+ {boosted_inc} (-> *edge-surface* fric)))",
                        'triggers': ['key', 'code', 'scan'],
                    },
                    {
                        'name': 'Gravity Increase',
                        'theme': 'Synonyms of "Ridiculous"',
                        'command': f"(set! (-> *standard-dynamics* gravity-length) (* (-> *standard-dynamics* gravity-length) {grav_mul}))",
                        'triggers': ['absurd', 'preposterous', 'ludicrous', 'outlandish', 'outrageous'],
                    },
                    {
                        'name': 'Gravity Decrease',
                        'theme': 'Done While Driving',
                        'command': f"(set! (-> *standard-dynamics* gravity-length) (/ (-> *standard-dynamics* gravity-length) {grav_mul}))",
                        'triggers': ['merge', 'brake', 'accelerate', 'signal', 'steer'],
                    },
                    {
                        'name': 'Low Poly',
                        'theme': 'Types of Wrenches',
                        'command': "(set! (-> *pc-settings* lod-force-tfrag) 2)(set! (-> *pc-settings* lod-force-tie) 3)(set! (-> *pc-settings* lod-force-ocean) 2)(set! (-> *pc-settings* lod-force-actor) 3)",
                        'command2': "(set! (-> *pc-settings* lod-force-tfrag) 0)(set! (-> *pc-settings* lod-force-tie) 0)(set! (-> *pc-settings* lod-force-ocean) 0)(set! (-> *pc-settings* lod-force-actor) 0)",
                        'triggers': ['pipe', 'monkey', 'socket', 'torque', 'combination', 'lug'],
                        'toggle': False
                    },
                    {
                        'name': 'No Rolljumps',
                        'theme': 'Team Fortress 2 Classes',
                        'command': "(set! (-> *TARGET-bank* wheel-jump-pre-window) (seconds 0))(set! (-> *TARGET-bank* wheel-jump-post-window) (seconds 0))",
                        'command2': "(set! (-> *TARGET-bank* wheel-jump-pre-window) (seconds 1))(set! (-> *TARGET-bank* wheel-jump-post-window) (seconds 0.1))",
                        'triggers': ['medic', 'spy', 'scout', 'heavy', 'engineer', 'soldier'],
                        'toggle': False
                    },
                    {
                        'name': 'Boosted Increase',
                        'theme': 'Before "Ware"',
                        'command': f"(set! (-> *edge-surface* fric) (- (-> *edge-surface* fric) {boosted_inc}))",
                        'triggers': ['silver', 'soft', 'hard', 'glass', 'firm'],
                    },
                    {
                        'name': 'Spin Radius Increase',
                        'theme': 'Internet Browsers',
                        'command': f"(set! (-> *TARGET-bank* spin-radius) (+ (meters {spin_inc}) (-> *TARGET-bank* spin-radius)))",
                        'triggers': ['opera', 'safari', 'chrome', 'edge'],
                    },
                    {
                        'name': 'No Daxter',
                        'theme': 'Types of Energy',
                        'command': "(send-event *target* 'sidekick #f)",
                        'command2': "(send-event *target* 'sidekick #t)",
                        'triggers': ['kinetic', 'potential', 'thermal', 'chemical'],
                        'toggle': False
                    },
                    {
                        'name': 'Short Fall',
                        'theme': 'Deodorants',
                        'command': "(set! (-> *TARGET-bank* fall-far) (meters 7))(set! (-> *TARGET-bank* fall-far-inc) (meters 15))",
                        'command2': "(set! (-> *TARGET-bank* fall-far) (meters 30))(set! (-> *TARGET-bank* fall-far-inc) (meters 20))",
                        'triggers': ['degree', 'axe', 'dove', 'spice'],
                        'toggle': False
                    },
                    {
                        'name': 'poop',
                        'theme': 'poop',
                        'command': "",
                        'triggers': ['poop'],
                    },
                    {
                        'name': 'Rapid Fire',
                        'theme': 'Wildcard 1',
                        'command': "(set! (-> *TARGET-bank* yellow-projectile-speed) (meters 100))(set! (-> *TARGET-bank* yellow-attack-timeout) (seconds 0))",
                        'triggers': ['stain']
                    },
                    {
                        'name': 'Back 2 Geyser',
                        'theme': 'Wildcard 2',
                        'command': "(start 'play (get-continue-by-name *game-info* \"intro-start\"))(auto-save-command 'auto-save 0 0 *default-pool*)",
                        'triggers': ['refuse', 'prevent'],
                    },
                    {
                        'name': 'Cell Bundle 1',
                        'theme': 'Wildcard 3',
                        'command': f"(set! (-> *game-info* fuel)(max {min_cell_count} (+ (-> *game-info* fuel) {cell_bundle})))",
                        'triggers': ['position'],
                    },
                    {
                        'name': 'Cell Bundle 2',
                        'theme': 'Wildcard 4',
                        'command': f"(set! (-> *game-info* fuel)(max {min_cell_count} (+ (-> *game-info* fuel) {cell_bundle})))",
                        'triggers': ['discard'],
                    },
                    {
                        'name': 'Cell Bundle 3',
                        'theme': 'Wildcard 5',
                        'command': f"(set! (-> *game-info* fuel)(max {min_cell_count} (+ (-> *game-info* fuel) {cell_bundle})))",
                        'triggers': ['torch'],
                    },
                    {
                        'name': 'Cell Bundle 4',
                        'theme': 'Wildcard 6',
                        'command': f"(set! (-> *game-info* fuel)(max {min_cell_count} (+ (-> *game-info* fuel) {cell_bundle})))",
                        'triggers': ['preach'],
                        
                    },
                    {
                        'name': 'Cell Bundle 5',
                        'theme': 'Wildcard 7',
                        'command': f"(set! (-> *game-info* fuel)(max {min_cell_count} (+ (-> *game-info* fuel) {cell_bundle})))",
                        'triggers': ['weasel'],
                    },
                    {
                        'name': 'Cell Drain 1',
                        'theme': 'Wildcard 8',
                        'command': f"(set! (-> *game-info* fuel)(max {min_cell_count} (- (-> *game-info* fuel) {cell_drain})))",
                        'triggers': ['static'],
                    },
                    {
                        'name': 'Cell Drain 2',
                        'theme': 'Wildcard 9',
                        'command': f"(set! (-> *game-info* fuel)(max {min_cell_count} (- (-> *game-info* fuel) {cell_drain})))",
                        'triggers': ['handle'],
                    },
                    {
                        'name': 'Cell Drain 3',
                        'theme': 'Wildcard 10',
                        'command': f"(set! (-> *game-info* fuel)(max {min_cell_count} (- (-> *game-info* fuel) {cell_drain})))",
                        'triggers': ['proper'],
                    },
                ]
        self.effects_found = {}
        self.max_matches = int(os.getenv('MAX_MATCHES', 0))
        self.count_sequence = 1
        self.message_barrier = 1
        self.target_count = int(os.getenv('COUNT_TARGET', 20))
        self.user_cooldown_limit = int(os.getenv('USER_COUNT_COOLDOWN', 3))
        self.count_reward = int(os.getenv('COUNT_REWARD', 2))
        self.max_count_reward = int(os.getenv('MAX_COUNT_REWARD', 5))
        self.count_count = 0
        self.recent_users = []
        self.blacklist = os.getenv("USER_BLACKLIST", "").lower().split(",")
        self.goalc_process = None
        self.gk_process = None
        self.clientSocket = None
        self.active = False

        # Register the cleanup function to be called at exit
        atexit.register(self.cleanup)

        # Load progress from file
        self.load_progress()

    def load_progress(self):
        """Load progress from the progress.env file."""
        try:
            if os.path.exists("progress.env"):
                with open("progress.json", "r") as file:
                    data = json.load(file)
                    self.effects_found = data.get("effects_found", {})
                    self.count_count = data.get("count_count", 0)
                print("Progress loaded successfully.")
            else:
                print("No progress file found. Starting fresh.")
        except Exception as e:
            print(f"Error loading progress: {e}")

    def save_progress(self):
        """Save progress to the progress.json file."""
        try:
            data = {
                "effects_found": self.effects_found,
                "count_count": self.count_count,
            }
            with open("progress.json", "w") as file:
                json.dump(data, file)
            print("Progress saved successfully.")
        except Exception as e:
            print(f"Error saving progress: {e}")

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
        # Start goalc.exe and gk.exe when bot is ready
        await self.launch_game()

    # Handle incoming messages in the chat
    async def event_message(self, message):
        # Ignore messages from the bot itself, unless they are commands
        if (message.author.name.lower() == channel.lower() and not chat_test) and not message.content.startswith('!'):
            return  # Ignore other messages from the bot itself

        chat_message = message.content.lower().strip()
        print(f"Received message: {chat_message}")
        
        # Check if the message is a valid number for the sequence
        await self.check_count_sequence(chat_message, message.author.name)

        # Check for start and stop commands
        if chat_message == "!startgame" and message.author.name.lower() in mods:
            self.active = True
            await self.send_message(channel, "🟢 Word processing started!")
            speak("Word processing started!")
            return
        elif chat_message == "!stopgame" and message.author.name.lower() in mods:
            self.active = False
            await self.send_message(channel, "🛑 Word processing stopped!")
            return

        # Process custom command for showing found words for an effect
        if chat_message.startswith('!'):
            await self.handle_custom_commands(chat_message, message.author.name)
            return

        # Only process messages if active
        if self.active and message.author.name not in self.blacklist:
            user = message.author.name
            await self.handle_chat_message(chat_message, user)
            
    async def check_count_sequence(self, chat_message, user):
        """Check if chat is counting correctly in sequence and reward if target reached."""
        #user = random.choice(self.effects[2]['triggers'])
        if not self.active or self.count_count >= self.max_count_reward or user == channel:
            return

        try:
            # Attempt to convert the message to an integer
            number = int(chat_message)
            print(user)
            #if number == 1 and self.count_sequence == 1:
            #    await self.send_message(channel, "🔥 Sequence started.")
            
            # Check if the number matches the expected count
            if number == self.count_sequence:
                if user in self.recent_users:
                    # If the user is among the last four users, don't allow counting
                    if self.count_sequence > self.message_barrier:
                        await self.send_message(channel, f"❌ Sequence broken due to repeat user ({user}).")
                    self.count_sequence = 1
                    self.recent_users = []
                    return

                if number == self.target_count:
                    # Reward a power cell if the target count is reached
                    polarity = "" if self.count_reward < 0 else "+"
                    response = "Power Cell!" if abs(self.count_reward) == 1 else "Power Cells!"
                    await self.send_message(channel, f"🎉 Chat reached {self.target_count} in sequence! {polarity}{self.count_reward} {response} 🎉")
                    self.send_form(f"(set! (-> *game-info* fuel)(max {min_cell_count} (+ (-> *game-info* fuel) {self.count_reward})))")
                    self.count_count += 1
                    speak(f"Chat reached {self.target_count} in sequence!")

                    # Reset sequence and recent users list
                    self.count_sequence = 1
                    self.recent_users = []
                else:
                    # Increment the sequence for the next expected number and update recent users
                    self.count_sequence += 1
                    self.recent_users.append(user)
                    
                    if len(self.recent_users) > self.user_cooldown_limit:
                        self.recent_users.pop(0)

            else:
                if self.count_sequence > self.message_barrier:
                    await self.send_message(channel, "❌ Sequence broken due to nonsequential number.")
                self.count_sequence = 1
                self.recent_users = []
            print(self.recent_users)

        except ValueError:
            if self.count_sequence > self.message_barrier:
                await self.send_message(channel, "❌ Sequence broken due to non-number.")
            self.count_sequence = 1
            self.recent_users = []

    # Handle chat messages and word processing
    async def handle_chat_message(self, chat_message, user):
        matches = 0
        for effect in self.effects:
            # Initialize the effect in self.effects_found if not already done
            if effect['name'] not in self.effects_found:
                self.effects_found[effect['name']] = {'words': [], 'completed': False}

            for trigger in effect['triggers']:
                if matches >= self.max_matches and self.max_matches > 0:
                    break
                # Determine if the trigger is a list (multiple alternatives) or a single word
                if isinstance(trigger, list):
                    # For a list, check if any alternative word exists in the message
                    match = any(re.search(r'\b' + re.escape(word) + r'\b', chat_message) for word in trigger)
                    main_word = trigger[0]  # Use the first word in the list as the unique identifier
                else:
                    # For a single word trigger
                    match = re.search(r'\b' + re.escape(trigger) + r'\b', chat_message)
                    main_word = trigger

                # If there is a match and the word hasn't been used already
                if match and main_word not in self.effects_found[effect['name']]['words']:
                    await self.trigger_effect(effect, main_word, user)

                    self.effects_found[effect['name']]['words'].append(main_word)
                    self.save_progress()

                    remaining_words = len(effect['triggers']) - len(self.effects_found[effect['name']]['words'])
                    await self.send_message(channel, f"🎯 {user} found {effect['name']} with '{main_word}' ({len(self.effects_found[effect['name']]['words'])}/{len(effect['triggers'])})!")

                    speak(f"{user} found {effect['name']} with '{main_word}'")
                    
                    if not tts:
                        await asyncio.sleep(2.5)
                        
                    matches += 1

            # Check if all words for this effect have been found, and give the reward if not already completed
            if len(self.effects_found[effect['name']]['words']) == len(effect['triggers']) and not self.effects_found[effect['name']]['completed']:
                await self.send_message(channel, f"🏆 All words found for {effect['name']} ({effect['theme']})!")
                self.send_form(f"(set! (-> *game-info* fuel)(max {min_cell_count} (+ (-> *game-info* fuel) {cell_inc})))")

                speak(f"All words found for {effect['name']} -- ({effect['theme']})!")

                self.effects_found[effect['name']]['completed'] = True
                self.save_progress()


    # Handle chat commands, including requests for showing found words for an effect and listing all effects
    async def handle_custom_commands(self, command, user):
        command = command.strip().lower()

        # Check if the command corresponds to a specific effect
        for effect in self.effects:
            effect_command = "!" + re.sub(r'[^a-zA-Z0-9]', '', effect['name']).lower()  # Make a clean command (e.g., "!speedboost")

            if command == effect_command:
                # Gather all found words for the effect
                effect_data = self.effects_found.get(effect['name'], {'words': [], 'completed': False})
                found_words = effect_data['words']

                # If no words have been found, skip showing the message
                if not found_words:
                    return

                # Show all found words
                found_words_str = ", ".join(found_words)
                total_words = len(effect['triggers'])
                completed_status = f" ({effect['theme']})" if effect_data['completed'] else f" ({len(effect_data['words'])}/{len(effect['triggers'])})"
                await self.send_message(channel, f"📝 {effect['name']}: {found_words_str}{completed_status}")
                return

        # Handle !effects command to show only unfinished effects
        if command == "!effects":
            not_completed_effects = []

            # Only include effects that are not completed and have at least one word found
            for effect_name, effect_data in self.effects_found.items():
                if not effect_data['completed'] and effect_data['words']:
                    found_count = len(effect_data['words'])
                    total_count = len(next(effect for effect in self.effects if effect['name'] == effect_name)['triggers'])
                    not_completed_effects.append(f"{effect_name} ({found_count}/{total_count})")

            # Respond appropriately
            if not self.effects_found:
                await self.send_message(channel, "❎ No effects found yet.")
            elif not not_completed_effects:
                await self.send_message(channel, "✅ All found effects are completed!")
            else:
                not_completed_list = ", ".join(not_completed_effects)
                await self.send_message(channel, f"🕒 Not Completed: {not_completed_list}")

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

    # Launch goalc.exe and gk.exe asynchronously, and monitor their statuses
    async def launch_game(self):
        try:
            self.gk_process = subprocess.Popen(['gk.exe', '-v', '--', '-boot', '-fakeiso', '-debug'], cwd=os.getcwd())
            
            # Wait for a moment to ensure gk.exe initializes properly
            await asyncio.sleep(2)
            
            self.goalc_process = subprocess.Popen(['goalc.exe'], cwd=os.getcwd())
            
            # Optionally, wait for the goalc process to initialize
            await asyncio.sleep(2)

            # Set up the socket connection to goalc.exe here if necessary
            self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.clientSocket.connect(("127.0.0.1", 8181))

            # Receive initial data (if applicable)
            data = self.clientSocket.recv(1024)
            print(data.decode())

            self.send_form('(lt)')
            self.send_form('(mi)')
            self.send_form("(set! *debug-segment* #f)")
            self.send_form("(set! *cheat-mode* #f)")
            self.send_form("(set! (-> *pc-settings* speedrunner-mode?) #f)")

            # Start an asyncio task to monitor the subprocesses
            asyncio.create_task(self.monitor_subprocesses())
            await self.send_message(channel, "🤖 Bot connected! plink")

        except Exception as e:
            print(f"Error launching gk or goalc: {e}")
            self.cleanup()
            sys.exit(1)

    async def monitor_subprocesses(self):
        """Monitor subprocesses asynchronously and terminate the program if any subprocess closes."""
        while True:
            goalc_status = self.goalc_process.poll()
            gk_status = self.gk_process.poll()

            if goalc_status is not None:
                print("goalc.exe has terminated.")
                break

            if gk_status is not None:
                print("gk.exe has terminated.")
                break

            await asyncio.sleep(1)  # Sleep briefly to avoid high CPU usage

        # If we break out of the loop (i.e., one of the subprocesses terminated), call cleanup and exit
        self.cleanup()
        sys.exit(1)

    def send_form(self, form):
        header = struct.pack('<II', len(form), 10)
        self.clientSocket.sendall(header + form.encode())
        print("Sent: " + form)

# Initialize and run the bot
bot = TwitchBot()
bot.run()