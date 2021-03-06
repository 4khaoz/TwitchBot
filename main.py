from twitchio.ext import commands, routines
from dotenv import load_dotenv

import os
import json
import asyncio

load_dotenv()

# CREDENTIALS
TMI_TOKEN = os.getenv('TWITCH_TOKEN')
CLIENT_ID = os.getenv('CLIENT_ID')
BOT_NICK = os.getenv('BOT_NAME')
BOT_PREFIX = os.getenv('BOT_PREFIX')
CHANNELS = os.getenv('CHANNELS').split(",")

CAP = int(os.getenv('CAP'))
WINRATE = int(os.getenv('WINRATE'))
LOSERATE = int(os.getenv('LOSERATE'))

viewers = {}

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(
            token=TMI_TOKEN, 
            client_id=CLIENT_ID, 
            prefix=BOT_PREFIX,
            nick=BOT_NICK,
            initial_channels=CHANNELS
        )

    async def event_ready(self):
        # Bot is ready
        print(f"Logged in as {self.nick}")
        await self.update.start()

    async def event_message(self, ctx: commands.Context):
        # bot ignores itself
        if ctx.author.name.lower() == BOT_NICK.lower():
            return

        await bot.handle_commands(ctx)

    @commands.command()
    async def hello(self, ctx: commands.Context):
        await ctx.send(f"Hello {ctx.author.name}!")

    @commands.command()
    async def points(self, ctx: commands.Context):
        # Load from JSON
        viewers = readJSON(ctx.channel.name)

        name = ctx.author.name.lower()
        if name not in viewers:
            await ctx.send(f"@{ctx.author.name} You don't have points.")
            return

        # Number of Points
        num = int(viewers[name]["points"])

        await ctx.send(f"@{ctx.author.name} You have {num} points")

    @commands.command()
    async def gamble(ctx, stake: int = 10):
        # Load Stats for Viewer
        viewers = readJSON(ctx.channel.name)
        name = ctx.author.name.lower()

        if name not in viewers:
            await ctx.send(f"@{ctx.author.name} You can't gamble yet.")
            return
    
        # Default Stats for Viewer
        stats = viewers[name]

        # Check if viewer has enough Money
        if stats["points"] < stake:
            await ctx.send(f"@{ctx.author.name} You don't have enough points.")
            return

        # GAMBLING MECHANICS
        rng = randrange(0, 100)

        msg = f"Draw! No points gained or lost."

        # WIN
        if rng < WINRATE:
            profit = stake * 2
            stats["points"] += profit

            msg = f"You won! +{profit} points!"        
            
        # LOSE
        elif rng >= CAP - LOSERATE:
            stats["points"] -= stake
            
            msg = f"You lost! -{stake} points!"

        # Save new Stats to file
        writeJSON(ctx.channel.name, viewers, name, stats)

        await ctx.send(msg)


    """
    Read from JSON-File
    """
    def readJSON(self, chnl: str):
        try:
            file = chnl.lower() + "_tracker.json"
            with open(file, 'r') as tracker:
                temp = json.load(tracker)
                return temp
        except:
            print("No tracker.json")
            return {}


    """
    Write to JSON-File
    """
    def writeJSON(self, chnl:str, viewerlist, key: str, value):
        file = chnl.lower() + "_tracker.json"
        with open(file, 'w') as tracker:
            viewerlist[key.lower()] = value
            json.dump(viewerlist, tracker, sort_keys=True, indent=4)


    """
    Async Loop to update Points for Viewers
    """
    @routines.routine(seconds=10)
    async def update(self):
        # For each tracked channel
        for ch in CHANNELS:
            viewers = self.readJSON(ch)
            try:
                # Why dafuq does this property only return the bot???
                chatterslist = self.get_channel(ch).chatters
                print(chatterslist)

                # Update for each Viewer connected to Chat
                for viewer in chatterslist:
                    v = viewer.name.lower()
                    print(v)
                    stats = {
                        "points": 0,
                    }

                    if v != BOT_NICK and v in viewers:
                        stats = viewers[v]

                    stats["points"] += 10
                    self.writeJSON(ch, viewers, v, stats)

            except Exception as e:
                print(e)
        
        # Update every 5 Minutes
        print("update")


bot = Bot()
bot.run()