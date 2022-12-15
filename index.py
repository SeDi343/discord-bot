#!/usr/bin/env python3
"""
# Discord Bot Template
"""
# Imports
import requests
import sys
import io
import aiohttp
from discord import app_commands, Intents, Client, Interaction, Embed, File

# Read Token from token file
with open('token', 'r') as file:
    token = file.read().rstrip()

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


async def _init_command_hello_response(interaction: Interaction) -> None:
   """A simple hello response from the Bot"""

   # Responds in the console that the command has been ran
   print(f"> {interaction.user} used the hello command.")

   # Respond with a simple hello
   await interaction.response.send_message("\n".join([
      f"Hi {interaction.user.mention}, thank you for saying hello!",
      "",
      "A charming Merry Christmas to you :)",
   ]))

async def _init_command_starwars_response(interaction: Interaction) -> None:
    """A function to response with a starwars meme"""

    # Responds in the console that the command has been ran
    print(f"> {interaction.user} used the starwars command.")

    async with aiohttp.ClientSession() as session:
        async with session.get("https://media.discordapp.net/attachments/732222852606066788/1052919738034045008/fc5ed98c2b4952971ec03a495fc85d73.png") as resp:
            if resp.status != 200:
                return await interaction.response.send_message("Could not download file...")
            data = io.BytesIO(await resp.read())
            await interaction.response.send_message(file=File(data, "star_wars.png"))

    """
    # Respond with the meme
    embed = Embed()
    embed.set_image(url="https://media.discordapp.net/attachments/732222852606066788/1052919738034045008/fc5ed98c2b4952971ec03a495fc85d73.png")
    await interaction.response.send_message(embed=embed)
    """

@client.tree.command()
async def hello(interaction: Interaction):
   """A new hello defined by me"""
   # Calls the function "_init_command_simple_response" to respond to the command
   await _init_command_hello_response(interaction)

@client.tree.command()
async def starwars(interaction: Interaction):
    """Send a starwars meme as response"""
    await _init_command_starwars_response(interaction)


# Runs the bot with the token you provided
client.run(token)
