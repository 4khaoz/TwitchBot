from twitchio.ext import commands
from dotenv import load_dotenv

import os

load_dotenv()

# CREDENTIALS
TMI_TOKEN = os.getenv('TWITCH_TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
BOT_NICK = os.getenv('BOT_NAME')
BOT_PREFIX = os.getenv('BOT_PREFIX')
CHANNELS = os.getenv('CHANNELS').split(",")

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            irc_token=TMI_TOKEN, 
            client_id=CLIENT_ID, 
            prefix=BOT_PREFIX,
            nick=BOT_NICK,
            initial_channels=CHANNELS
        )

    async def event_ready(self):
        # Bot is ready
        print(f"Logged in as {self.nick}")

    @commands.command()
    async def hello(self, ctx):
        await ctx.send(f"Hello {ctx.author.name}!")


bot = Bot()
bot.run()