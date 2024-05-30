# main module for the discord bot
# initialize the bot and set commands as needed

import discord
from discord.ext import commands
from dotenv import load_dotenv
import stats
import os
import player as pl
import asyncio
import secrets
import datetime
import aiohttp
import botutils
from discord import ButtonStyle, SelectOption
from discord.ui import Button, View, Select, Modal, TextInput

load_dotenv()
token = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


# set containers

@bot.event
async def on_ready():
    print('ready')

# Define a function to start the bot
async def start_bot():
    await bot.start(token)

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


class ConfirmationModal(Modal):
    def __init__(self, title="Enter the correct value"):
        super().__init__(title=title)
        self.add_item(TextInput(label="Value:", placeholder="Enter the correct value"))

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Your Modal Results", color=discord.Color.blurple())
        embed.add_field(name="Corrected Value", value=self.children[0].value, inline=False)
        await interaction.response.send_message(embed=embed)

        

class StatCorrectionSelect(discord.ui.Select):
    def __init__(self, player):
        options = [
            discord.SelectOption(label="Name", description="Correct the player's name"),
            discord.SelectOption(label="Kills", description="Correct the number of kills"),
            discord.SelectOption(label="Deaths", description="Correct the number of deaths"),
            discord.SelectOption(label="Assists", description="Correct the number of assists"),
        ]
        super().__init__(placeholder="Select the stat to correct", min_values=1, max_values=1, options=options)
        self.player = player

    async def callback(self, interaction: discord.Interaction):
        selected_stat = self.values[0]
        modal = ConfirmationModal()
        await interaction.response.send_modal(modal)

class PlayerSelect(discord.ui.Select):
    def __init__(self, team1_info, team2_info):
        options = [
            discord.SelectOption(label=player, description="Team 1") for player in team1_info
        ] + [
            discord.SelectOption(label=player, description="Team 2") for player in team2_info
        ]
        super().__init__(placeholder="Choose a player to correct", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_player = self.values[0]
        self.view.clear_items()
        self.view.add_item(StatCorrectionSelect(selected_player))
        await interaction.response.edit_message(content=f"You selected {selected_player}. What needs correction?", view=self.view)

class ConfirmationView(discord.ui.View):
    def __init__(self, user_id, team1_info, team2_info):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.team1_info = team1_info
        self.team2_info = team2_info

    @discord.ui.button(label="Yes", style=ButtonStyle.green, custom_id="confirm_yes")
    async def confirm_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Thank you for confirming the stats!", ephemeral=True)

    @discord.ui.button(label="No", style=ButtonStyle.red, custom_id="confirm_no")
    async def confirm_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.clear_items()
        self.add_item(PlayerSelect(self.team1_info, self.team2_info))
        await interaction.response.edit_message(content="Please choose the player and stat that needs correction.", view=self)

# Usage example, function to initiate the interaction
async def confirm_stats(user_id, team1_info, team2_info):
    user = await bot.fetch_user(user_id)
    if user:
        dm_channel = await user.create_dm()
        message_team1 = botutils.format_player_stats(team1_info)
        message_team2 = botutils.format_player_stats(team2_info)
        view = ConfirmationView(user_id, team1_info, team2_info)
        await dm_channel.send(f"**Team 1 Stats:**\n{message_team1}\n**Team 2 Stats:**\n{message_team2}", view=view)


# obtain correction from user mid-pipeline
async def prompt_correction(user_id, extracted_name):
    user = await bot.fetch_user(user_id)
    if user:
        dm_channel = await user.create_dm()
        message = (f"OCR extracted the name '{extracted_name}'. "
                   "Please reply with the correct name.")
        await dm_channel.send(message)

@bot.command(name='upload', help='Fetch a screenshot from users and provide an access code.')
async def upload_image(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("You do not have permission to perform this action.")
        return

    # Generate a temporary access code
    access_code = secrets.token_urlsafe(8)  # Generates a secure random token

    # Send the access code to the user's DM
    try:
        await ctx.author.send(f"Your access code is {access_code}. It will expire in 5 minutes.")
        await ctx.send("Access code sent to your DMs.")

        # Prepare to send the access code and user ID to the backend
        backend_url = 'http://127.0.0.1:8000/store_access_code/'
        json_data = {
            'user_id': str(ctx.author.id),
            'access_code': access_code
        }

        # Send data to backend using aiohttp
        async with aiohttp.ClientSession() as session:
            headers = {'Content-Type': 'application/json'}  # Ensuring headers are set
            async with session.post(backend_url, json=json_data, headers=headers) as response:
                if response.status == 200:
                    print("Access code successfully sent to backend.")
                else:
                    print("Failed to send access code to backend.")
                    await ctx.send("Failed to process access code.")
    except Exception as e:
        print(f"Error: {str(e)}")
        await ctx.send("Failed to send DM. Please check your DM settings.")
