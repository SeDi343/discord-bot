#!/usr/bin/env python3
"""
# Discord Bot Template
"""
# Imports
import sys
import requests
import json
import io
import aiohttp
import asyncpraw
import asyncio
from discord import app_commands, Intents, Client, Interaction, Embed, File

# Read config file
with open("config.json", 'r') as jsonfile:
    config_data = json.load(jsonfile)
    token = config_data.get("token")

# Check if Token is valid
r = requests.get("https://discord.com/api/v10/users/@me", headers={
    "Authorization": f"Bot {token}"
})

# If the token is correct, it will continue the code
data = r.json()

if not data.get("id", None):
    print("\n".join(["ERROR: Token is not valid!"]))
    sys.exit(False)


# Welcome in console
print("\n".join([
    "Starting Discord Bot..."
]))


# Main Class to response in Discord
class ChatResponse(Client):
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        """ This is called when the bot boots, to setup the global commands """
        await self.tree.sync(guild=None)


# Variable to store the bot class and interact with it
# Since this is a simple bot to run 1 command over slash commands
# We then do not need any intents to listen to events
client = ChatResponse(intents=Intents.none())


@client.event
async def on_ready():
    """ This is called when the bot is ready and has a connection with Discord
        It also prints out the bot's invite URL that automatically uses your
        Client ID to make sure you invite the correct bot with correct scopes.
    """
    print("\n".join([
        f"Logged in as {client.user} (ID: {client.user.id})",
        "",
        f"Use this URL to invite {client.user} to your server:",
        f"https://discord.com/api/oauth2/authorize?client_id={client.user.id}&scope=applications.commands%20bot"
    ]))


# Function for a Hello
async def _init_command_hello_response(interaction: Interaction) -> None:
   """A hello response from the Bot"""

   # Respond in the console that the command has been ran
   print(f"> {interaction.user} used the hello command.")

   # Respond with a simple hello
   await interaction.response.send_message("\n".join([
      f"Hi {interaction.user.mention}, thank you for saying hello!",
      "",
      "A charming Merry Christmas to you :)",
   ]))

# Function for Star Wars
async def _init_command_starwars_response(interaction: Interaction) -> None:
    """A function to response with a starwars meme"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.user} used the starwars command.")

    async with aiohttp.ClientSession() as session:
        async with session.get("https://media.discordapp.net/attachments/732222852606066788/1052919738034045008/fc5ed98c2b4952971ec03a495fc85d73.png") as resp:
            if resp.status != 200:
                return await interaction.response.send_message("Could not download file...")
            data = io.BytesIO(await resp.read())
            await interaction.response.send_message(file=File(data, "star_wars.png"))

# Function for a Meme from r/memes
async def _init_command_meme_response(interaction: Interaction) -> None:
    """A function to send a random meme using reddit api"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.user} used the meme command.")


    # Tell Discord that Request takes some time
    await interaction.response.defer()

    # Reddit API Session
    try:
        #async with aiohttp.ClientSession(trust_env=True) as reddit_session:
        async with aiohttp.ClientSession() as reddit_session:
            reddit = asyncpraw.Reddit(
                client_id = config_data.get("client_id"),
                client_secret = config_data.get("client_secret"),
                redirect_uri = config_data.get("redirect_uri"),
                requestor_kwargs = {"session": reddit_session},
                user_agent = config_data.get("user_agent"),
                check_for_async=False)
            reddit.read_only = True

            # Respond with a meme from reddit
            subreddit = await reddit.subreddit("memes")
            submission = await subreddit.random()

            # Convert Submission into picture and send it to Discord
            await interaction.followup.send(submission.url)
    except:
        return await interaction.followup.send("Could not send picture...")


async def _init_command_gif_response(interaction: Interaction) -> None:
    """A function to send a random gif using reddit api"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.user} used the gif command.")


    # Tell Discord that Request takes some time
    await interaction.response.defer()

    # Reddit API Session
    try:
        #async with aiohttp.ClientSession(trust_env=True) as reddit_session:
        async with aiohttp.ClientSession() as reddit_session:
            reddit = asyncpraw.Reddit(
                client_id = config_data.get("client_id"),
                client_secret = config_data.get("client_secret"),
                redirect_uri = config_data.get("redirect_uri"),
                requestor_kwargs = {"session": reddit_session},
                user_agent = config_data.get("user_agent"),
                check_for_async=False)
            reddit.read_only = True

            # Respond with a meme from reddit
            subreddit = await reddit.subreddit("gifs")
            submission = await subreddit.random()

            # Convert Submission into picture and send it to Discord
            await interaction.followup.send(submission.url)
    except:
        return await interaction.followup.send("Could not send gif...")


# Command for Hello
@client.tree.command()
async def hello(interaction: Interaction):
   """A simple hello as a return"""
   # Calls the function "_init_command_simple_response" to respond to the command
   await _init_command_hello_response(interaction)

# Command for Star Wars
@client.tree.command()
async def starwars(interaction: Interaction):
    """Send a starwars meme as response"""
    await _init_command_starwars_response(interaction)

# Command for a Meme from r/memes
@client.tree.command()
async def meme(interaction: Interaction):
    """Send a random meme using reddit api"""
    await _init_command_meme_response(interaction)

# Command for a GIF from r/gifs
@client.tree.command()
async def gif(interaction: Interaction):
    """Send a random gif using reddit api"""
    await _init_command_gif_response(interaction)


# Runs the bot with the token you provided
client.run(token)
