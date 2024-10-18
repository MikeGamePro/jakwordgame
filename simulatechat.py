import os
import asyncio
import atexit
from twitchio.ext import commands
from dotenv import load_dotenv

# Load environment variables from chatgame.env
load_dotenv(dotenv_path='chatgame.env')

# Fetch OAuth token and channel from environment variables
oauth_token = os.getenv('TWITCH_OAUTH_TOKEN')
channel = os.getenv('TWITCH_USERNAME')

class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=oauth_token, prefix='!', initial_channels=[channel])
        self.clientSocket = None
        atexit.register(self.cleanup)

        # List of messages to send
        self.messages = ['grant', 'warthog', 'mongoose', 'elephant', 'mammoth', 'scorpion', 'falcon', 'rhino', 'pelican', 'hornet', 'well', 'bat', 'lead', 'light', 'spring', 'match', 'date', 'bowl', 'seal']

    def cleanup(self):
        if self.clientSocket:
            self.clientSocket.close()
            print("Closed client socket.")

    # Event: When the bot connects to Twitch chat
    async def event_ready(self):
        print(f'Logged in as | {channel}')
        print(f'Connected to channel | {self.connected_channels}')

        # Start sending messages from the list every second
        await self.send_messages_from_list()

    # Send messages from the list every second
    async def send_messages_from_list(self):
        if self.connected_channels:
            for msg in self.messages:
                await self.connected_channels[0].send(msg)
                await asyncio.sleep(0.5)  # Wait for 1 second before sending the next message

    # Event: When a message is received
    async def event_message(self, message):
        if message.author.name.lower() == channel.lower():
            return

        # Proceed with processing the message
        chat_message = message.content.lower().strip()
        print(f"Received message: {chat_message}")

        # Store the username of the sender
        user = message.author.name

    # Helper to send a single message
    async def send_message(self, channel_name, message):
        """Send a message to the channel."""
        channel = self.get_channel(channel_name)
        if channel:
            await channel.send(f"-> {message}")

# Initialize and run the bot
bot = TwitchBot()
bot.run()
