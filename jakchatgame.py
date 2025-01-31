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

# Load environment variables from settings.env
load_dotenv(dotenv_path='settings.env')

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

# Load effects from JSON file
def load_effects():
    with open('effects.json', 'r') as file:
        effects = json.load(file)
    return effects

class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=oauth_token, prefix='!', initial_channels=[channel])
        self.words_used = set()
        self.simulate_users = False  # Simulate different users
        self.effects = load_effects()
        self.effects_found = {}
        self.max_matches = int(os.getenv('MAX_MATCHES', 0))
        self.count_sequence = 1
        self.message_barrier = 1
        self.target_count = int(os.getenv('COUNT_TARGET', 20))
        self.user_cooldown_limit = int(os.getenv('USER_COUNT_COOLDOWN', 3))
        self.count_reward = int(os.getenv('COUNT_REWARD', 2))
        self.max_count_rewards = int(os.getenv('MAX_COUNT_REWARDS', 5))
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
        """Load progress from the progress.json file."""
        try:
            if os.path.exists("progress.json"):
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
        if self.simulate_users:
            user = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))  # Generate a random username

        if not self.active or self.count_count >= self.max_count_rewards or user == channel:
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
        command = effect['command']
        
        # Dictionary of attributes and their corresponding values
        attributes = {
            '{random_death}': random.choice(death_list),
            '{random_boom}': random.choice(boom_list),
            '{random_point}': point_list[random.choice(range(0,52))],
            '{min_cell_count}': str(min_cell_count),
            '{cell_inc}': str(cell_inc),
            '{cell_bundle}': str(cell_bundle),
            '{cell_drain}': str(cell_drain),
            '{orb_inc}': str(orb_inc),
            '{speed_inc}': str(speed_inc),
            '{jump_inc}': str(jump_inc),
            '{slip_res_inc}': str(slip_res_inc),
            '{size_inc}': str(size_inc),
            '{blue_eco_inc}': str(blue_eco_inc),
            '{rolljump_inc}': str(rolljump_inc),
            '{boosted_inc}': str(boosted_inc),
            '{iframes_inc}': str(iframes_inc),
            '{spin_inc}': str(spin_inc),
            '{grav_mul}': str(grav_mul)
        }

        for attribute, value in attributes.items():
            command = command.replace(attribute, value)

        if 'toggle' in effect and effect['toggle']:
            effect['toggle'] = False
            command_to_send = effect['command2']
        else:
            command_to_send = command
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