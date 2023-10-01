#!/usr/bin/env python3.11
# Imports
import os
import sys
import re
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
import random
import traceback
import timeit
from datetime import datetime, timedelta, timezone
from discord import app_commands, Intents, Client, Interaction, File, Object, Embed, Status, Game, utils

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

# Guild IDs
feierabend_id = 1047547059433119774

# Main Class to response in Discord
class ChatResponse(Client):
    def __init__(self):
        super().__init__(intents = Intents.all())
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

    await client.tree.sync(guild = Object(id = feierabend_id))
    await client.change_presence(status=Status.online, activity=Game(name="/help | aerography.eu"))

#########################################################################################
# Functions
#########################################################################################

# Function to check out all available commands
async def _init_command_help_response(interaction):
    """The function to check help"""
    try:
        # Respond in the console that the command has been ran
        print(f"> {interaction.guild} : {interaction.user} used the help command.")

        await interaction.response.send_message("\n".join([
            f"Available Commands for {client.user.mention}:",
            "**\\help** - Shows this Message.",
            "**\\hello** - A simple hello response.",
            "**\\starwarsstatic** - A static Star Wars Meme.",
            "**\\reddit string** - A random post from given reddit subreddit.",
            "**\\meme** - A random post from r/memes.",
            "**\\starwars** - A random post from r/starwarsmemes.",
            "**\\gif** - A random post from r/gifs.",
            "**\\art** - A random post from r/art.",
            "**\\dataisbeautiful** - A random post from r/dataisbeautiful.",
            "**\\qod** - The Quote of the Day.",
            "**\\quote** - A random Quote",
            f"**\\donation** - A link to support the creator of {client.user.mention}",
            "**And many other Discord Server specific Commands!**"
        ]))
    except Exception:
        print(f" > Exception occured processing help command: {traceback.format_exc()}")
        return await interaction.response.send_message(f"Can not process help command. Please contact <@164129430766092289> when this happened.")


# Function for exception response
def console_create(traceback):
    embed = Embed(title="Traceback")
    embed.set_footer(text=re.sub(r'File ".*[\\/]([^\\/]+.py)"',r'File "\1"', traceback.format_exc()))
    return embed

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
        raise Exception("Thousands of subreddits go dark protesting Reddit's new API Costs")
        #t_0 = timeit.default_timer()
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

            #t_1 = timeit.default_timer()

            algorithm = 2

            # Check if Subreddit exists
            try:
                subreddit = [sub async for sub in reddit.subreddits.search_by_name(subreddit_string, exact=True)]
            except asyncprawcore.exceptions.NotFound:
                print(f" > Exception: Subreddit \"{subreddit_string}\" not found")
                await interaction.followup.send(f"Subreddit \"{subreddit_string}\" does not exist!")
                raise
            except asyncprawcore.exceptions.ServerError:
                print(f" > Exception: Reddit Server not reachable")
                await interaction.followup.send(f"Reddit Server not reachable!")
                raise

            if algorithm == 1:
                # Get Hot Submissions
                submission_limit = 200
                submissions = []
                random_number = random.randint(1,submission_limit-1)
                async for submission in subreddit[0].hot(limit=submission_limit):
                    submissions.append(submission)

                # Get a Random Submission
                submission = submissions[random_number]
            if algorithm == 2:
                submission = await subreddit[0].random()

            #t_2 = timeit.default_timer()
            #print(f" > Elapsed time init: {round((t_1 - t_0), 3)} sec")
            #print(f" > Elapsed time post: {round((t_2 - t_1), 3)} sec")

            # Return Random Submission
            return submission
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
        while extension not in(".jpg", ".png", ".gif", ".gifv"):
            submission = await _reddit_api_request(interaction, subreddit)

            # Check extension of submission url
            response = requests.get(submission.url, verify=os.path.dirname(__file__)+"/certs.pem")
            content_type = response.headers["content-type"]
            extension = mimetypes.guess_extension(content_type)
            if extension in(".jpg", ".png", ".gif", ".gifv"):
                break

        # Send Content in Discord
        await interaction.followup.send(submission.url)
    except Exception:
        print(f" > Exception occured processing reddit: {traceback.format_exc()}")
        await interaction.followup.send(f"Exception occured processing reddit. Please contact <@164129430766092289> when this happened.")
        return await interaction.channel.send(embed=console_create(traceback))


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
        print(f" > Exception occured processing meme: {traceback.format_exc()}")
        await interaction.followup.send(f"Exception occured processing meme. Please contact <@164129430766092289> when this happened.")
        return await interaction.channel.send(embed=console_create(traceback))


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
        while extension not in(".jpg", ".png", ".gif", ".gifv"):
            submission = await _reddit_api_request(interaction, "starwarsmemes")

            # Check extension of submission url
            response = requests.get(submission.url, verify=os.path.dirname(__file__)+"/certs.pem")
            content_type = response.headers["content-type"]
            extension = mimetypes.guess_extension(content_type)
            if extension in(".jpg", ".png", ".gif", ".gifv"):
                break

        # Send Content in Discord
        await interaction.followup.send(submission.url)
    except Exception:
        print(f" > Exception occured processing starwars: {traceback.format_exc()}")
        await interaction.followup.send(f"Exception occured processing starwars. Please contact <@164129430766092289> when this happened.")
        return await interaction.channel.send(embed=console_create(traceback))


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
        print(f" > Exception occured processing gif: {traceback.format_exc()}")
        await interaction.followup.send(f"Exception occured processing gif. Please contact <@164129430766092289> when this happened.")
        return await interaction.channel.send(embed=console_create(traceback))


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
        print(f" > Exception occured processing art: {traceback.format_exc()}")
        await interaction.followup.send(f"Exception occured processing art. Please contact <@164129430766092289> when this happened.")
        return await interaction.channel.send(embed=console_create(traceback))


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
        while extension not in(".jpg", ".png", ".gif", ".gifv"):
            submission = await _reddit_api_request(interaction, "dataisbeautiful")

            # Check extension of submission url
            response = requests.get(submission.url, verify=os.path.dirname(__file__)+"/certs.pem")
            content_type = response.headers["content-type"]
            extension = mimetypes.guess_extension(content_type)
            if extension in(".jpg", ".png", ".gif", ".gifv"):
                break

        # Send Content in Discord
        embed = Embed(title=submission.title)
        embed.set_image(url=submission.url)
        await interaction.followup.send(embed=embed)
    except Exception:
        print(f" > Exception occured processing dataisbeautiful: {traceback.format_exc()}")
        await interaction.followup.send(f"Exception occured processing dataisbeautiful. Please contact <@164129430766092289> when this happened.")
        return await interaction.channel.send(embed=console_create(traceback))


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
        print(f" > Exception occured processing qod: {traceback.format_exc()}")
        await interaction.followup.send(f"Exception occured processing qod. Please contact <@164129430766092289> when this happened.")
        return await interaction.channel.send(embed=console_create(traceback))


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
        print(f" > Exception occured processing quote: {traceback.format_exc()}")
        await interaction.followup.send(f"Exception occured processing quote. Please contact <@164129430766092289> when this happened.")
        return await interaction.channel.send(embed=console_create(traceback))


# Function for VIPs to check how many days they have left
async def _init_command_vipinfo_response(interaction: Interaction):
    """A function to check how many days a given user has left"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.guild} : {interaction.user} used the vipstatus command.")

    # Tell Discord that Request takes some time
    await interaction.response.defer()

    # Variable for Roles
    has_rights = False
    has_vip = False

    guild = client.get_guild(feierabend_id)
    mods_channel = client.get_channel(1049082386127790141)
    vip_role = utils.get(guild.roles, name="Feierabend VIPs")

    # Check if User has Discord Role "FEIERABEND VIPS" or "IM FEIERABEND :)"
    for role in interaction.user.roles:
        if role.name == "Feierabend VIPs" or "Im Feierabend :)":
            has_rights = True
        if role.name == "Feierabend VIPs":
            has_vip = True

    # Continue only when User has rights
    if has_rights:
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
                    if user is not None:
                        if guild.get_member_named(user) == interaction.user:
                            keyentry = key
                            break

                # Find remaining days for given User
                if keyentry == False and has_vip:
                    # If User was not found but has VIP Role
                    return await interaction.followup.send(f"{interaction.user.mention} you have VIP on this Server for a lifetime membership.")
                if keyentry == False and not(has_vip):
                    return await interaction.followup.send(f"{interaction.user.mention} it seems like you do not have VIP on this Server. Please Check out <#1047547059433119777> for more Information.")
                if keyentry != False:
                    # Send information how many days a user has VIP left if User was found
                    time_now = datetime.now()
                    time_end = pandas.to_datetime(excel_output["Unnamed: 4"].values[int(keyentry)])
                    steam_id = excel_output["Unnamed: 7"].values[int(key)]

                    time_left = time_end - time_now

                    if time_left.days >= -1:
                        # Check if VIP Role is not in Useres Roles List, and add it if it is not existent
                        if not vip_role in interaction.user.roles:
                            await interaction.user.add_roles(vip_role)
                        await interaction.followup.send(f"{interaction.user.mention} you have VIP for **{time_left.days + 1} {'day' if time_left.days == 0 else 'days'}** left!")
                    else:
                        await interaction.user.remove_roles(vip_role)
                        await interaction.followup.send(f"{interaction.user.mention} your VIP Status has **expired** since **{(time_left.days + 1) * -1} {'day' if time_left.days == -2 else 'days'}**!\nPlease Check out <#1047547059433119777> for more Information.")
                        await mods_channel.send(f"{interaction.user.mention} **{interaction.user}** his VIP has expired. Steam ID: **{steam_id}**")
        except Exception:
            print(f" > Exception occured processing vipstatus: {traceback.format_exc()}")
            await interaction.followup.send(f"Exception occured processing vipstatus. Please contact <@164129430766092289> when this happened.")
            return await interaction.channel.send(embed=console_create(traceback))
    # If User is not VIP
    else:
        return await interaction.followup.send(f"Insurficient Rights to use this Command")


# Function to check which users have expired VIP
async def _init_command_expiredvips_response(interaction: Interaction):
    """Function to check which users do not have VIP left"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.guild} : {interaction.user} used the expiredvips command.")

    # Tell Discord that Request takes some time
    await interaction.response.defer()

    # Variable for Rights
    has_rights = False

    # Check if User has enough Discord Rights
    for role in interaction.user.roles:
        if role.name == "Owner" or role.name == "Admin" or role.name == "Support":
            has_rights = True

    # Continue only when User has VIP
    if has_rights:
        try:
            # Required Variables default start Values
            return_string = ""
            time_now = datetime.now()
            guild = client.get_guild(feierabend_id)

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

                # Receive Discord Names
                discord_usernames = excel_json.get("Unnamed: 2")

                # For every row in Discord Names
                for key, discord_username in discord_usernames.items():
                    if int(key) >= 1:
                        # Receive Time End Date
                        if str(excel_output["Unnamed: 4"].values[int(key)]) != "00:00:00":
                            # Receive Time End Date
                            time_end_user = pandas.to_datetime(excel_output["Unnamed: 4"].values[int(key)])

                            # Calculate Time left
                            time_left_user = time_end_user - time_now

                            # Check if user has no time left if so, print it out
                            if time_left_user.days <= -1 and time_left_user.days >= -20:
                                game_username = excel_output["Unnamed: 1"].values[int(key)]
                                steam_id = excel_output["Unnamed: 7"].values[int(key)]
                                if discord_username is not None:
                                    member = guild.get_member_named(discord_username)
                                    if member is not None:
                                        return_string += f"User: **{game_username}** Steam: **{steam_id}** Discord: **{member.mention}** has expired since **{time_left_user.days + 1}** days!\n"
                                    else:
                                        return_string += f"User: **{game_username}** Steam: **{steam_id}** Discord: **{discord_username}** has expired since **{time_left_user.days + 1}** days!\n"
                                else:
                                    return_string += f"User: **{game_username}** Steam: **{steam_id}** Discord: **{discord_username}** has expired since **{time_left_user.days + 1}** days!\n"
                await interaction.followup.send(return_string)
        except Exception:
            print(f" > Exception occured processing expiredvips: {traceback.format_exc()}")
            await interaction.followup.send(f"Exception occured processing expiredvips. Please contact <@164129430766092289> when this happened.")
            return await interaction.channel.send(embed=console_create(traceback))
    # If User is not enough rights
    else:
        return await interaction.followup.send(f"It seems like you do not have the requested Rights")


# Function to update VIPs on Discord
async def _init_command_vipupdate_response(interaction: Interaction):
    """Function to update VIPs on Discord"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.guild} : {interaction.user} used the vipupdate command.")

    # Tell Discord that Request takes some time
    await interaction.response.defer()

    # Variable for Rights
    has_rights = False

    # Check if User has enough Discord Rights
    for role in interaction.user.roles:
        if role.name == "Owner" or role.name == "Admin" or role.name == "Support":
            has_rights = True

    # Continue only when User has VIP
    if has_rights:
        try:
            # Required Variables default start Values
            time_now = datetime.now()

            guild = client.get_guild(feierabend_id)
            role = utils.get(guild.roles, name="Feierabend VIPs")
            return_string_exp = ""
            return_string_act = ""

            counter_vip = 0
            counter_expvip = 0

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

                # Receive Discord Names
                discord_usernames = excel_json.get("Unnamed: 2")

                # For every row in Discord Names
                for key, discord_username in discord_usernames.items():
                    if int(key) >= 1:
                        # Check if End Date exists
                        if str(excel_output["Unnamed: 4"].values[int(key)]) != "00:00:00":
                            # Receive Time End Date
                            time_end_user = pandas.to_datetime(excel_output["Unnamed: 4"].values[int(key)])
                            steam_id = excel_output["Unnamed: 7"].values[int(key)]

                            # Calculate Time left
                            time_left_user = time_end_user - time_now

                            # Check if Discord User is existent
                            if discord_username is not None:
                                # Receive Discord User
                                member = guild.get_member_named(discord_username)
                                # Check if Discord User is still connected to Discord Guild
                                if member is not None:
                                    # Remove VIP Role if expired
                                    if time_left_user.days <= -1:
                                        await member.remove_roles(role)
                                        if time_left_user.days >= -10:
                                            return_string_exp += f"{member.mention} {steam_id} ({time_left_user.days + 1}) | "
                                        counter_expvip += 1
                                    # Add VIP Role otherwise
                                    else:
                                        await member.add_roles(role)
                                        if time_left_user.days <= 10:
                                            return_string_act += f"{member.mention} {steam_id} ({time_left_user.days + 1}) | "
                                        counter_vip += 1
                await interaction.followup.send(f"Updated VIP Role of Users. {counter_expvip} expired VIPs, {counter_vip} active VIPs\nActive (10 Days remaining):\n{return_string_act}\nInactive (Since 10 Days):\n{return_string_exp}")
        except Exception:
            print(f" > Exception occured processing viplist: {traceback.format_exc()}")
            await interaction.followup.send(f"Exception occured processing viplist. Please contact <@164129430766092289> when this happened.")
            return await interaction.channel.send(embed=console_create(traceback))
    # If User is not enough rights
    else:
        return await interaction.followup.send(f"It seems like you do not have the requested Rights")


# Function for Gameserver connect command response
async def _init_command_ip_response(interaction: Interaction):
    """A gameserver connect command response from the Bot"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.guild} : {interaction.user} used the ip command.")

    # Respond with the connection command
    await interaction.response.send_message("\n".join([
        f"Hey {interaction.user.mention}, following you find the commands for the F1 console to connect to the server",
        "",
        "**client.connect feierabend.aerography.eu:20000**"
    ]))


# Function to Vote for Rust Server on rust-servers.net
async def _init_command_vote_response(interaction: Interaction):
    """A simple vote command to vote on rust-servers.net"""

    # Respond in the console that the command has been ran
    print(f"> {interaction.guild} : {interaction.user} used the vote command.")

    # Repsond with the vote command
    await interaction.response.send_message("\n".join([
        f"Hey {interaction.user.mention}, follow this Link to vote for our Server:",
        "https://rust-servers.net/server/169062/vote/",
        "After voting you can use **/claim** ingame to receive a little gift."
    ]))


# Function to send donation response
async def _init_command_donation_response(interaction):
    """The function to send donation link"""
    try:
        # Respond in the console that the command has been ran
        print(f"> {interaction.guild} : {interaction.user} used the donation command.")

        await interaction.response.send_message("\n".join([
            f"Hey {interaction.user.mention}, thank you for considering donating to support my work!",
            f"You can donate via PayPal using https://donate.aerography.eu/ :heart_hands:"]))
    except Exception:
        print(f" > Exception occured processing donation command: {traceback.format_exc()}")
        await interaction.followup.send(f"Exception occured processing reddit. Please contact <@164129430766092289> when this happened.")
        return await interaction.channel.send(embed=console_create(traceback))

#########################################################################################
# Commands
#########################################################################################

# Command to check help
@client.tree.command()
async def help(interaction: Interaction):
    """Help Command for Music Bot"""
    await _init_command_help_response(interaction)

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
@client.tree.command(guild = Object(id = feierabend_id))
async def vipstatus(interaction: Interaction):
    """Command to check how many days a vip has left"""
    await _init_command_vipinfo_response(interaction)

# Command to check expired VIPs
@client.tree.command(guild = Object(id = feierabend_id))
async def expiredvips(interaction: Interaction):
    """Command to check which users do not have VIP left"""
    await _init_command_expiredvips_response(interaction)

# Command to update VIPs on Discord
@client.tree.command(guild = Object(id = feierabend_id))
async def vipupdate(interaction: Interaction):
    """"Command to update VIPs on Discord"""
    await _init_command_vipupdate_response(interaction)

# Command to check connect command for gameserver
@client.tree.command(guild = Object(id = feierabend_id))
async def ip(interaction: Interaction):
    """Command to check gameserver connect command"""
    await _init_command_ip_response(interaction)

# Command to vote for gameserver
@client.tree.command(guild = Object(id = feierabend_id))
async def vote(interaction: Interaction):
    """Command to vote for gameserver"""
    await _init_command_vote_response(interaction)

# Command for Donation
@client.tree.command()
async def donate(interaction: Interaction):
    """A command to send donation link"""
    await _init_command_donation_response(interaction)

#########################################################################################
# Server Start
#########################################################################################

# Runs the bot with the token you provided
client.run(token)
