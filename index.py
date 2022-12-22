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
import aiofiles
import dropbox
import pandas
from datetime import datetime, timedelta
from discord import app_commands, Intents, Client, Interaction, File, Object

#########################################################################################
# Requirements for Discord Bot
#########################################################################################

# Read config file
with open("config.json", 'r') as jsonfile:
    config_data = json.load(jsonfile)
    token = config_data.get("discord_token")

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
    def __init__(self):
        super().__init__(intents = Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        """ This is called when the bot boots, to setup the global commands """
        await self.tree.sync(guild = None)

# Variable to store the bot class and interact with it
# Since this is a simple bot to run 1 command over slash commands
# We then do not need any intents to listen to events
client = ChatResponse()

#########################################################################################
# Start Up
#########################################################################################

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

    await client.tree.sync(guild = Object(id = 1047547059433119774))


#########################################################################################
# Functions
#########################################################################################

# Function for a Hello
async def _init_command_hello_response(interaction: Interaction):
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
async def _init_command_starwars_response(interaction: Interaction):
    """A function to response with a starwars meme"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.user} used the starwars command.")

    async with aiohttp.ClientSession() as session:
        async with session.get("https://media.discordapp.net/attachments/732222852606066788/1052919738034045008/fc5ed98c2b4952971ec03a495fc85d73.png") as resp:
            if resp.status != 200:
                return await interaction.response.send_message("Could not download file...")
            data = io.BytesIO(await resp.read())
            await interaction.response.send_message(file=File(data, "star_wars.png"))


# Reddit API Function
async def _reddit_api_request(subreddit_string):
    try:
        #async with aiohttp.ClientSession(trust_env=True) as session:
        async with aiohttp.ClientSession() as session:
            reddit = asyncpraw.Reddit(
                client_id = config_data.get("reddit_client_id"),
                client_secret = config_data.get("reddit_client_secret"),
                redirect_uri = config_data.get("reddit_redirect_uri"),
                requestor_kwargs = {"session": session},
                user_agent = config_data.get("reddit_user_agent"),
                check_for_async=False)
            reddit.read_only = True

            # Respond with a meme from reddit
            subreddit = await reddit.subreddit(subreddit_string)
            return await subreddit.random()
    except:
        return False


# Function for a Meme from r/memes
async def _init_command_meme_response(interaction: Interaction):
    """A function to send a random meme using reddit api"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.user} used the meme command.")

    # Tell Discord that Request takes some time
    await interaction.response.defer()

    try:
        submission = await _reddit_api_request("meme")
        await interaction.followup.send(submission.url)
    except:
        return await interaction.followup.send("Could not send picture...")


# Function for a GIF from r/gifs
async def _init_command_gif_response(interaction: Interaction):
    """A function to send a random gif using reddit api"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.user} used the gif command.")

    # Tell Discord that Request takes some time
    await interaction.response.defer()

    try:
        submission = await _reddit_api_request("gifs")
        await interaction.followup.send(submission.url)
    except:
        return await interaction.followup.send("Could not send gif...")


# Function for an ART from r/art
async def _init_command_art_response(interaction: Interaction):
    """A function to send a random art using reddit api"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.user} used the art command.")

    # Tell Discord that Request takes some time
    await interaction.response.defer()

    try:
        submission = await _reddit_api_request("art")
        await interaction.followup.send(submission.url)
    except:
        return await interaction.followup.send("Could not send picture...")


# Function for VIPs to check how many days they have left
async def _init_command_vipinfo_response(interaction: Interaction):
    """A function to check how many days a given user has left"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.user} used the vipstatus command.")

    # Tell Discord that Request takes some time
    await interaction.response.defer()

    # Variable for VIP
    has_vip = False

    # Check if User has Discord Role "FEIERABEND VIPS"
    for role in interaction.user.roles:
        if role.name == "Feierabend VIPs":
            has_vip = True

    # Continue only when User has VIP
    if has_vip:
        try:
            # Read Config File
            async with aiofiles.open("config.json", 'r') as jsonfile:
                raw_json = await jsonfile.read()
                config_data = json.loads(raw_json)

            # Connect to Dropbox
            dropbox_cloud = dropbox.Dropbox(oauth2_access_token = config_data.get("dropbox_token"),
                                            oauth2_refresh_token = config_data.get("dropbox_refresh_token"),
                                            oauth2_access_token_expiration = datetime.strptime(config_data.get("dropbox_token_expire"), "%Y-%m-%d %H:%M:%S.%f"),
                                            app_key = config_data.get("dropbox_app_key"),
                                            app_secret = config_data.get("dropbox_app_secret"),
                                            user_agent = config_data.get("dropbox_user_agent"))

            # Check if Dropbox Access Token is still valid
            old_dropbox_token = dropbox_cloud._oauth2_access_token
            dropbox.Dropbox.check_and_refresh_access_token(dropbox_cloud)
            new_dropbox_token = dropbox_cloud._oauth2_access_token

            # If there is a new Dropbox Token available, save it into json and create new dropbox session
            if old_dropbox_token != new_dropbox_token:
                print(" > Dropbox Access Token is expired. Refreshing...")
                async with aiofiles.open("config.json", mode="w") as jsonfile:
                    config_data["dropbox_token"] = new_dropbox_token
                    config_data["dropbox_token_expire"] = str(datetime.utcnow() + timedelta(seconds=14400))
                    jsonstring = json.dumps(config_data, indent=4)
                    await jsonfile.write(jsonstring)

                # Create an new dropbox session
                dropbox_cloud = dropbox.Dropbox.clone(dropbox_cloud, oauth2_access_token = new_dropbox_token)

            dropbox_path = config_data.get("dropbox_filepath")

            # Download File
            async with aiofiles.open("temp.xlsx", mode="wb") as dropbox_file:
                _,dropbox_download = dropbox_cloud.files_download(dropbox_path)
                await dropbox_file.write(dropbox_download.content)

            # Read out File
            async with aiofiles.open("temp.xlsx", mode="rb") as dropbox_file:
                dropbox_content = await dropbox_file.read()
                dropbox_excel = pandas.read_excel(dropbox_content)
                excel_output = pandas.DataFrame(data=dropbox_excel)
                excel_json = json.loads(excel_output.to_json())

                # Find User based on Discord User in Excel Sheet
                keyentry = False

                discord_users = excel_json.get("Unnamed: 2")

                for key, user in discord_users.items():
                    # First 4 Entries are no valid Entries
                    if user == str(interaction.user) and int(key) >= 5:
                        keyentry = key
                        break

                # Find remaining days for given User
                if keyentry == False:
                    # If User was not found
                    return await interaction.followup.send(f"{interaction.user.mention} it seems like you no longer have VIP on this Server.")
                else:
                    # Send information how many days a user has VIP left if User was found
                    time_left = excel_json.get("Unnamed: 5", {}).get(str(keyentry))
                    await interaction.followup.send(f"{interaction.user.mention} has VIP for **{time_left}** days left!")
        except Exception as e:
            print(f" > Exception occured processing vipstatus: {e}")
            return await interaction.followup.send(f"Exception occured processing vipstatus. Please contact <@164129430766092289> when this happened.")

    # If User is not VIP
    else:
        return await interaction.followup.send(f"It seems like you do not have VIP on this Server")


#########################################################################################
# Commands
#########################################################################################

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

# Command for an art from r/art
@client.tree.command()
async def art(interaction: Interaction):
    """Send a random art using reddit api"""
    await _init_command_art_response(interaction)

# Command to check remaining days VIP
@client.tree.command(guild = Object(id = 1047547059433119774))
async def vipstatus(interaction: Interaction):
    """Command to check how many days a vip has left"""
    await _init_command_vipinfo_response(interaction)

#########################################################################################
# Server Start
#########################################################################################

# Runs the bot with the token you provided
client.run(token)
