# main module for the discord bot
# initialize the bot and set commands as needed

import discord
from discord.ext import commands
from dotenv import load_dotenv
import stats
import os
import player as pl
import asyncio
import quickstart
import aiohttp
import storage_service

load_dotenv()
token = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)
client = discord.Client()

# set containers
teams = []

@bot.event
async def on_ready():
    print('ready')

# command: !player
@bot.command(name= 'player', help='Displays stats for a specified player.')
async def player_stats(ctx, playerName: str):

    player_row = stats.get_row(playerName)
    if player_row is None:
        await ctx.send("name not found")
    else:
        current_player = pl.Player(player_row)
        # we have the player object, embed
        embed = discord.Embed(title=current_player.get_name(), color=0x00ff00)
        embed.add_field(name="Level:", value=str(current_player.get_level()), inline=True)
        embed.add_field(name="Ranked Stats:", value=current_player.get_rank(), inline=True)
        embed.add_field(name="Tournament KD:", value=current_player.get_tournamentKD(), inline=False)
        embed.add_field(name="Tournament W/L:", value=current_player.get_WL(), inline=False)
        embed.add_field(name="Finals Record:", value=current_player.get_finalsApp(), inline=False)
        await ctx.send(embed=embed)

# command: !fraudwatch
@bot.command(name='fraudwatch', help='Determines who is under fraud watch')
async def fraud_watch(ctx):

    fraud_watch_list = stats.fraud_watch()
    names_str = ""
    vals_str = ""
    embed = discord.Embed(title="SOON TO BE FRAUDS", color=0x00ff00)
    for name, diff in fraud_watch_list.items():
        names_str += f"{name}\n"
        vals_str += f"{diff}\n"
    
    embed.add_field(name="Name:", value=names_str, inline=True)
    embed.add_field(name="KD Differential:", value=vals_str, inline=True)
    await ctx.send(embed=embed)





# command: !carried
@bot.command(name='carried', help='Determine which players are carried.')
async def get_carried(ctx):

    carried = stats.get_carried_players()
    names_str = ""
    win_rate_str = ""
    kd_str = ""
    embed = discord.Embed(title="CARRIED PLAYERS", color=0x00ff00)
    for name, list in carried.items():
        names_str += f"{name}\n"
        win_rate_str += f"{list[1]}\n"
        kd_str += f"{list[0]}\n"
    embed.add_field(name="Name:", value=names_str, inline=True)
    embed.add_field(name="T-KD:", value=kd_str, inline=True)
    embed.add_field(name="Win Rate:", value=win_rate_str, inline=True)
    await ctx.send(embed=embed)


# command: !frauds
@bot.command(name='frauds', help='Determines who the current fraudulent players are.')
async def get_frauds(ctx):

    frauds = stats.det_frauds()
    names_str = ""
    vals_str = ""
    embed = discord.Embed(title="FRAUDULENT PLAYERS", color=0x00ff00)
    for name, diff in frauds.items():
        names_str += f"{name}\n"
        vals_str += f"{diff}\n"
    
    embed.add_field(name="Name:", value=names_str, inline=True)
    embed.add_field(name="KD Differential:", value=vals_str, inline=True)
    await ctx.send(embed=embed)




# command: !odds
@bot.command(name='odds', help='Calculates and displays odds for a match.')
async def match_odds(ctx, *, matchInfo: str):

    if len(teams) < 2:
        await ctx.send("Less than 2 teams in memory")
    else:
        team1Name, team2Name = matchInfo.split()
        team1 = find_team(team1Name)
        team2 = find_team(team2Name)
        odds = team1.get_score() - team2.get_score()
        await ctx.send(odds)

# command: !compare
@bot.command(name='compare', help='Compare two players.')
async def compare(ctx, *, names : str):
    
    name1, name2 = names.split()
    player1_row = stats.get_row(name1)
    player2_row = stats.get_row(name2)
    player1_str = pl.Player(player1_row).toString()
    player2_str = pl.Player(player2_row).toString()
    embed = discord.Embed(title="Player Comparison", color=0x00ff00)
    stat_names = ""
    for stat in player1_row.keys():
        stat_names += f"**{stat}**\n"
    embed.add_field(name=f"__{name1}__", value=player1_str, inline=True)
    embed.add_field(name=f"Stats", value=stat_names, inline=True)
    embed.add_field(name=f"__{name2}__", value=player2_str, inline=True)
    await ctx.send(embed=embed)

# obtain correction from user mid-pipeline
async def prompt_correction(user_id, extracted_name, suggestions):
    user = await client.fetch_user(user_id)
    if user:
        dm_channel = await user.create_dm()
        message = (f"OCR extracted the name '{extracted_name}'. "
                   f"Suggestions: {', '.join(suggestions)}. "
                   "Please reply with the correct name.")
        await dm_channel.send(message)


# command: !streamerinfo
@bot.command(name='streamerinfo', help='Provide information regarding streamer contract(s).')
async def streamer(ctx):

    await ctx.send("Want to become a streamer for the org?")


# command: !mosscheck
@bot.command(name='mosscheck', help='Queue a team for moss checking.')
async def queue_moss(ctx, team_number= int):

    # handle invalid team_number parameter
    if not isinstance(team_number, int):
        await ctx.send("Please enter a whole number.")
    elif team_number > len(teams) or team_number < 1:
        await ctx.send("Team number out of range.")
    
    # authenticate credentials
    service = quickstart.auth_credentials()
    await ctx.send(f"MOSS file submission window for Team {team_number} is now open. You have 15 minutes to upload your files.")
    await asyncio.sleep(600)
    # extract files
    extracted_files = quickstart.get_log_files(service, team_number)
    if len(extracted_files) >= 5:
        # code for pos case
        await ctx.send("idl")
    else:
        missing = 5 - len(extracted_files)
        await ctx.send(f"MISSING {missing} MOSS FILES FOR TEAM {team_number}. POTENTIAL PENALTY INCOMING.")
    
    
    # time is up check that all files are present

# command: !upload
@bot.command(name='upload', help='Fetch a screenshot from users.')
async def upload_image(ctx):
    user_id = ctx.message.author.id
    if not ctx.message.attachments:
        await ctx.send("Please attach an image.")
        return

    attachment = ctx.message.attachments[0]
    image_url = attachment.url

    # Upload the image directly from URL to Google Cloud Storage
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status != 200:
                await ctx.send("Failed to download image.")
                return
            # Read image as stream
            data = await response.read()
            file_name_in_gcs = f'images/{attachment.filename}'
            try:
                # Upload stream data to Google Cloud Storage
                public_image_url = await storage_service.upload_stream_to_gcs(data, file_name_in_gcs)
                web_tool_url = f"http://yourwebtool.com/edit?image={public_image_url}"
                await ctx.send(f"Edit your image here: {web_tool_url}")
            except Exception as e:
                await ctx.send(f"Failed to upload image: {str(e)}")
            
    
    # send screenshot to the front end and process or whatever.



def find_team(name: str):

    for team in teams:
        if team.get_name().lower() == name.lower():
            return team
    return None

bot.run(token) 