#!/usr/bin/env python3.11
# Imports
import os
import sys
import requests
import mimetypes
import json
import io
import aiohttp
import asyncpraw
import asyncprawcore
import aiofiles
import dropbox
import pandas
import traceback
from datetime import datetime, timedelta
from discord import app_commands, Intents, Client, Interaction, File, Object, Embed, Status, Game

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
    await client.change_presence(status=Status.online, activity=Game(name="May the Force be with you!"))


#########################################################################################
# Functions
#########################################################################################

# Function for a Hello
async def _init_command_hello_response(interaction: Interaction):
   """A hello response from the Bot"""

   # Respond in the console that the command has been ran
   print(f"> {interaction.guild} : {interaction.user} used the hello command.")

   # Respond with a simple hello
   await interaction.response.send_message("\n".join([
      f"Hi {interaction.user.mention}, thank you for saying hello!",
      "",
      "<@164129430766092289> and I wish you a wonderful and Happy New Year \U0001F386\U0001F973\U0001F340\U0001F942!",
   ]))


# Function for Star Wars
async def _init_command_starwars_static_response(interaction: Interaction):
    """A function to response with a starwars meme"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.guild} : {interaction.user} used the starwars stattic command.")

    async with aiohttp.ClientSession() as session:
        async with session.get("https://media.discordapp.net/attachments/732222852606066788/1052919738034045008/fc5ed98c2b4952971ec03a495fc85d73.png") as resp:
            if resp.status != 200:
                return await interaction.response.send_message("Could not download file...")
            data = io.BytesIO(await resp.read())
            await interaction.response.send_message(file=File(data, "star_wars.png"))


# Reddit API Function
async def _reddit_api_request(interaction: Interaction, subreddit_string: str):
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

            # Check if Subreddit exists
            try:
                subreddit = [sub async for sub in reddit.subreddits.search_by_name(subreddit_string, exact=True)]
            except asyncprawcore.exceptions.NotFound:
                print(f" > Exception: Subreddit \"{subreddit_string}\" not found")
                await interaction.followup.send(f"Subreddit \"{subreddit_string}\" does not exist!")
                raise

            # Respond with content from reddit
            subreddit = await reddit.subreddit(subreddit_string)
            return await subreddit.random()
    except Exception:
        raise


# Function for a picture, gif from any given subreddit
async def _init_command_reddit_response(interaction: Interaction, subreddit: str):
    """A function to send a picture, gif from any given subreddit"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.guild} : {interaction.user} used the reddit \"{subreddit}\" command.")

    # Tell Discord that Request takes some time
    await interaction.response.defer()

    # Check if parameter is a string
    if not isinstance(subreddit, str):
        return await interaction.followup.send(f"Exception, Parameter needs to be a string")

    try:
        extension = None

        # Make sure the extension of the URL is jpg, png or gif
        while extension not in(".jpg", ".png", ".gif"):
            submission = await _reddit_api_request(interaction, subreddit)

            # Check extension of submission url
            response = requests.get(submission.url, verify=os.path.dirname(__file__)+"/certs.pem")
            content_type = response.headers["content-type"]
            extension = mimetypes.guess_extension(content_type)

        # Send Content in Discord
        await interaction.followup.send(submission.url)
    except Exception:
        print(f" > Exception occured processing reddit: {traceback.print_exc()}")
        return await interaction.followup.send(f"Exception occured processing reddit. Please contact <@164129430766092289> when this happened.")


# Function for a Meme from r/memes
async def _init_command_meme_response(interaction: Interaction):
    """A function to send a random meme using reddit api"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.guild} : {interaction.user} used the meme command.")

    # Tell Discord that Request takes some time
    await interaction.response.defer()

    try:
        submission = await _reddit_api_request(interaction, "meme")
        await interaction.followup.send(submission.url)
    except Exception:
        print(f" > Exception occured processing meme: {traceback.print_exc()}")
        return await interaction.followup.send(f"Exception occured processing meme. Please contact <@164129430766092289> when this happened.")


# Function for a Star Wars Meme from r/starwarsmemes
async def _init_command_starwars_response(interaction: Interaction):
    """A function to send a random star wars meme using reddit api"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.guild} : {interaction.user} used the starwars command.")

    # Tell Discord that Request takes some time
    await interaction.response.defer()

    try:
        extension = None

        # Make sure the extension of the URL is jpg, png or gif
        while extension not in(".jpg", ".png", ".gif"):
            submission = await _reddit_api_request(interaction, "starwarsmemes")

            # Check extension of submission url
            response = requests.get(submission.url, verify=os.path.dirname(__file__)+"/certs.pem")
            content_type = response.headers["content-type"]
            extension = mimetypes.guess_extension(content_type)

        # Send Content in Discord
        await interaction.followup.send(submission.url)
    except Exception:
        print(f" > Exception occured processing starwars: {traceback.print_exc()}")
        return await interaction.followup.send(f"Exception occured processing starwars. Please contact <@164129430766092289> when this happened.")


# Function for a GIF from r/gifs
async def _init_command_gif_response(interaction: Interaction):
    """A function to send a random gif using reddit api"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.guild} : {interaction.user} used the gif command.")

    # Tell Discord that Request takes some time
    await interaction.response.defer()

    try:
        submission = await _reddit_api_request(interaction, "gifs")
        await interaction.followup.send(submission.url)
    except Exception:
        print(f" > Exception occured processing gif: {traceback.print_exc()}")
        return await interaction.followup.send(f"Exception occured processing gif. Please contact <@164129430766092289> when this happened.")


# Function for an ART from r/art
async def _init_command_art_response(interaction: Interaction):
    """A function to send a random art using reddit api"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.guild} : {interaction.user} used the art command.")

    # Tell Discord that Request takes some time
    await interaction.response.defer()

    try:
        submission = await _reddit_api_request(interaction, "art")
        await interaction.followup.send(submission.url)
    except Exception:
        print(f" > Exception occured processing art: {traceback.print_exc()}")
        return await interaction.followup.send(f"Exception occured processing art. Please contact <@164129430766092289> when this happened.")


# Function for an Picture of r/dataisbeautiful
async def _init_command_data_response(interaction: Interaction):
    """A function to send a random data using reddit api"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.guild} : {interaction.user} used the dataisbeautiful command.")

    # Tell Discord that Request takes some time
    await interaction.response.defer()

    try:
        extension = None

        # Make sure the extension of the URL is jpg, png or gif
        while extension not in(".jpg", ".png", ".gif"):
            submission = await _reddit_api_request(interaction, "dataisbeautiful")

            # Check extension of submission url
            response = requests.get(submission.url, verify=os.path.dirname(__file__)+"/certs.pem")
            content_type = response.headers["content-type"]
            extension = mimetypes.guess_extension(content_type)

        # Send Content in Discord
        embed = Embed(title=submission.title)
        embed.set_image(url=submission.url)
        await interaction.followup.send(embed=embed)
    except Exception:
        print(f" > Exception occured processing dataisbeautiful: {traceback.print_exc()}")
        return await interaction.followup.send(f"Exception occured processing dataisbeautiful. Please contact <@164129430766092289> when this happened.")


# Function to receive quote of the day
async def _init_command_qod_response(interaction: Interaction):
    """A function to send a qod quote"""

    # Repsond in the console that the command has ben ran
    print(f"> {interaction.guild} : {interaction.user} used the qod command.")

    # Tell Discord that Request takes some time
    await interaction.response.defer()

    try:
        async with aiohttp.ClientSession() as session:
            quote_url = "https://zenquotes.io/api/today"
            async with session.get(quote_url) as response:
                if response.status == 200:
                    quote = await response.json()
                    quote_str = quote[0].get("q")
                    author_str = quote[0].get("a")
                    await interaction.followup.send(f"{quote_str} - {author_str}")
                else:
                    await interaction.followup.send(f"{response.status}: Could not send quote of the day...")
    except Exception:
        print(f" > Exception occured processing qod: {traceback.print_exc()}")
        return await interaction.followup.send(f"Exception occured processing qod. Please contact <@164129430766092289> when this happened.")


# Function to receive a random quote
async def _init_command_quote_response(interaction: Interaction):
    """A function to send a random quote """

    # Repsond in the console that the command has ben ran
    print(f"> {interaction.guild} : {interaction.user} used the quote command.")

    # Tell Discord that Request takes some time
    await interaction.response.defer()

    try:
        async with aiohttp.ClientSession() as session:
            quote_url = "https://zenquotes.io/api/random"
            async with session.get(quote_url) as response:
                if response.status == 200:
                    quote = await response.json()
                    quote_str = quote[0].get("q")
                    author_str = quote[0].get("a")
                    await interaction.followup.send(f"{quote_str} - {author_str}")
                else:
                    await interaction.followup.send(f"{response.status}: Could not send quote...")
    except Exception:
        print(f" > Exception occured processing quote: {traceback.print_exc()}")
        return await interaction.followup.send(f"Exception occured processing quote. Please contact <@164129430766092289> when this happened.")


# Function for VIPs to check how many days they have left
async def _init_command_vipinfo_response(interaction: Interaction):
    """A function to check how many days a given user has left"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.guild} : {interaction.user} used the vipstatus command.")

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
                dropbox_excel = pandas.read_excel(dropbox_content, header=3)
                excel_output = pandas.DataFrame(data=dropbox_excel)
                excel_json = json.loads(excel_output.to_json())

                # Find User based on Discord User in Excel Sheet
                keyentry = False

                discord_users = excel_json.get("Unnamed: 2")

                for key, user in discord_users.items():
                    if user == str(interaction.user):
                        keyentry = key
                        break

                # Find remaining days for given User
                if keyentry == False:
                    # If User was not found
                    return await interaction.followup.send(f"{interaction.user.mention} you no longer have VIP on this Server or have a lifetime membership.")
                else:
                    # Send information how many days a user has VIP left if User was found
                    time_now = datetime.utcnow()
                    time_end = pandas.to_datetime(excel_output["Unnamed: 4"].values[int(keyentry)])

                    time_left = time_end - time_now

                    if time_left.days >= -1:
                        await interaction.followup.send(f"{interaction.user.mention} you have VIP for **{time_left.days + 1} {'day' if time_left.days == 0 else 'days'}** left!")
                    else:
                        await interaction.followup.send(f"{interaction.user.mention} your VIP Status has **expired** since **{(time_left.days + 1) * -1} {'day' if time_left.days == -2 else 'days'}**!")
        except Exception:
            print(f" > Exception occured processing vipstatus: {traceback.print_exc()}")
            return await interaction.followup.send(f"Exception occured processing vipstatus. Please contact <@164129430766092289> when this happened.")
    # If User is not VIP
    else:
        return await interaction.followup.send(f"It seems like you do not have VIP on this Server")


# Function for Gameserver connect command response
async def _init_command_ip_response(interaction: Interaction):
    """A gameserver connect command response from the Bot"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.guild} : {interaction.user} used the ip command.")

    # Respond with the connection command
    await interaction.response.send_message("\n".join([
        f"Hey {interaction.user.mention}, following you find the commands for the F1 console to connect to the server",
        "",
        "**client.connect gameserver.rust-feierabend.de:25000**"
    ]))


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
async def starwarsstatic(interaction: Interaction):
    """Send a starwars meme as response"""
    await _init_command_starwars_static_response(interaction)

@client.tree.command()
async def reddit(interaction: Interaction, subreddit: str):
    """Send a picture, gif from given subreddit"""
    await _init_command_reddit_response(interaction, subreddit)

# Command for a Meme from r/memes
@client.tree.command()
async def meme(interaction: Interaction):
    """Send a random meme using reddit api"""
    await _init_command_meme_response(interaction)

@client.tree.command()
async def starwars(interaction: Interaction):
    """Send a starwars meme using reddit api"""
    await _init_command_starwars_response(interaction)

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

# Command for a picture from r/dataisbeautiful
@client.tree.command()
async def dataisbeautiful(interaction: Interaction):
    """Send a random picture from dataisbeautiful using reddit api"""
    await _init_command_data_response(interaction)

# Command for quote of the day
@client.tree.command()
async def qod(interaction: Interaction):
    """Send the quote of the day"""
    await _init_command_qod_response(interaction)

# Command for a random quote
@client.tree.command()
async def quote(interaction: Interaction):
    """Send a random quote"""
    await _init_command_quote_response(interaction)

# Command to check remaining days VIP
@client.tree.command(guild = Object(id = 1047547059433119774))
async def vipstatus(interaction: Interaction):
    """Command to check how many days a vip has left"""
    await _init_command_vipinfo_response(interaction)

# Command to check connect command for gameserver
@client.tree.command(guild = Object(id = 1047547059433119774))
async def ip(interaction: Interaction):
    """Command to check gameserver connect command"""
    await _init_command_ip_response(interaction)

#########################################################################################
# Server Start
#########################################################################################

# Runs the bot with the token you provided
client.run(token)
