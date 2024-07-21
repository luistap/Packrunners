# main module for the discord bot
# initialize the bot and set commands as needed

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import secrets
import aiohttp
import botutils
from discord import ButtonStyle
from discord.ui import View, Select, Modal, TextInput
from stats_manager import global_stats_manager
import asyncpg

load_dotenv()
token = os.getenv('TOKEN')
channel_send = 880977932892385330

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

correction_completed_event = asyncio.Event()
pool = None

async def init_db():
    global pool
    try:
        pool = await asyncpg.create_pool(
            database="packrunnerDB",
            user="packrunnerDB_owner",
            password="GXJyfgEB23nj",
            host="ep-hidden-king-a5h5vm2e.us-east-2.aws.neon.tech",
            ssl="require"
        )
        print("Connection pool created successfully")
    except Exception as e:
        print(f"Failed to create pool: {e}")

async def fetch_data():
    try:
        async with pool.acquire() as conn:
            async with conn.transaction():
                result = await conn.fetch("SELECT * FROM some_table")
                return result
    except Exception as e:
        print(f"An error occurred during fetching data: {e}")
        return None

@bot.command(name='getdata')
async def get_data(ctx):
    data = await fetch_data()
    if data:
        message = "\n".join([str(row) for row in data])
        await ctx.send(message)
    else:
        await ctx.send("Failed to fetch data or no data found.")

@bot.event
async def on_ready():
    await init_db()
    print('Bot is ready and connected to the database!')

@bot.event
async def on_close():
    global pool
    if pool:
        await pool.close()
        print("Connection pool closed")

# Define a function to start the bot
async def start_bot():
    await bot.start(token)


async def post_match_summary(team1_info, team2_info, gen_info):
    channel = bot.get_channel(channel_send)
    if channel:
        # Format the message
        message = f"**Match Summary:**\n**Map:** {gen_info[0]}\n**Match Type:** {gen_info[1]}\n**Score:** {gen_info[2]}\n\n"
        message += "**Team 1 Stats:**\n"
        for player, stats in team1_info.items():
            message += f"{player}: Kills: {stats[0]}, Deaths: {stats[1]}, Assists: {stats[2]}\n"
        message += "\n**Team 2 Stats:**\n"
        for player, stats in team2_info.items():
            message += f"{player}: Kills: {stats[0]}, Deaths: {stats[1]}, Assists: {stats[2]}\n"

        # Send the message
        await channel.send(message)

@bot.command(name='h2h', help='Get the head-to-head record between two players')
async def h2h(ctx, player1: str, player2: str):
    # Ensure the database connection
    connection = await asyncpg.connect(
            database="packrunnerDB",
            user="packrunnerDB_owner",
            password="GXJyfgEB23nj",
            host="ep-hidden-king-a5h5vm2e.us-east-2.aws.neon.tech",
            ssl="require"
        )


    # Fetch the H2H record
    record = await fetch_h2h_record(connection, player1, player2)
    if record:
        await ctx.send(f"{record['player_one_name']} is {record['player_one_wins']}-{record['player_two_wins']} against {record['player_two_name']} all time")
    else:
        await ctx.send("No head-to-head record found between these players.")

    # Close the database connection
    await connection.close()

async def fetch_h2h_record(connection, player1, player2):
    # Get IDs for both players
    player1_id = await connection.fetchval("SELECT player_id FROM Players WHERE name = $1", player1)
    player2_id = await connection.fetchval("SELECT player_id FROM Players WHERE name = $1", player2)

    if not player1_id or not player2_id:
        return None  # If either player ID is not found, return None

    # Fetch H2H records, considering both potential orderings of player IDs
    query = """
        SELECT 
            p1.name as player_one_name, 
            p2.name as player_two_name, 
            h.player_one_wins, 
            h.player_two_wins
        FROM H2H_Records h
        JOIN Players p1 ON h.player_one_id = p1.player_id
        JOIN Players p2 ON h.player_two_id = p2.player_id
        WHERE (h.player_one_id = $1 AND h.player_two_id = $2) 
           OR (h.player_one_id = $2 AND h.player_two_id = $1)
    """
    record = await connection.fetchrow(query, player1_id, player2_id)

    return record



@bot.command(name='player', help='Get player stats')
async def player_stats(ctx, player_name: str):
    try:
        async with pool.acquire() as conn:
            async with conn.transaction():
                # Assuming you have a table called 'player_stats' with columns 'name', 'kills', 'deaths', etc.
                query = "SELECT name, kills, deaths, assists FROM player_stats WHERE name = $1"
                result = await conn.fetchrow(query, player_name)

                if result:
                    message = (f"Stats for {result['name']}:\n"
                               f"Kills: {result['kills']}\n"
                               f"Deaths: {result['deaths']}\n"
                               f"Assists: {result['assists']}")
                else:
                    message = f"No stats found for {player_name}."
    except Exception as e:
        print(f"An error occurred: {e}")
        message = "Failed to fetch player stats."

    await ctx.send(message)


class ConfirmationModal(Modal):
    def __init__(self, title="Enter the correct value", player=None, team1_info=None, team2_info=None, selected_stat=None):
        super().__init__(title=title)
        self.player = player
        self.selected_stat = selected_stat
        self.team1_info = team1_info
        self.team2_info = team2_info
        self.add_item(TextInput(label="Value:", placeholder="Enter the correct value"))

    async def on_submit(self, interaction: discord.Interaction):
        corrected_value = self.children[0].value
        # Determine which team the player is in and the index for the stat
        team = 'team1' if self.player in global_stats_manager.get_team_info('team1') else 'team2'
        stat_indices = {'Kills': 0, 'Deaths': 1, 'Assists': 2}
        
        if self.selected_stat in stat_indices:
            # For numerical stats like Kills, Deaths, Assists
            stat_index = stat_indices[self.selected_stat]
            global_stats_manager.update_stat(team, self.player, stat_index, int(corrected_value))
        elif self.selected_stat == "Name":
            # Special case for updating names
            global_stats_manager.update_name(team, corrected_value, self.player)
            
        embed = discord.Embed(title="Your Modal Results", color=discord.Color.blurple())
        embed.add_field(name="Corrected Value", value=corrected_value, inline=False)
        embed.add_field(name="Updated stats: Team 1", value=botutils.format_player_stats(global_stats_manager.get_team_info('team1')), inline=False)
        embed.add_field(name="Updated stats: Team 2", value=botutils.format_player_stats(global_stats_manager.get_team_info('team2')), inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        # Reinstate the confirmation view to allow further corrections
        view = ConfirmationView(interaction.user.id, self.team1_info, self.team2_info)
        await interaction.followup.send("Would you like to make more corrections?", view=view)

class StatCorrectionSelect(Select):
    def __init__(self, player, team1_info, team2_info):
        self.player = player
        self.team1_info = team1_info
        self.team2_info = team2_info
        options = [
            discord.SelectOption(label="Name", description="Correct the player's name"),
            discord.SelectOption(label="Kills", description="Correct the number of kills"),
            discord.SelectOption(label="Deaths", description="Correct the number of deaths"),
            discord.SelectOption(label="Assists", description="Correct the number of assists"),
        ]
        super().__init__(placeholder="Select the stat to correct", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_stat = self.values[0]
        modal = ConfirmationModal(title=f"Correcting {selected_stat} for {self.player}", 
                                  player=self.player, team1_info=self.team1_info, team2_info=self.team2_info, selected_stat=self.values[0])
        await interaction.response.send_modal(modal)

class PlayerSelect(Select):
    def __init__(self, team1_info, team2_info):
        self.team1_info = team1_info
        self.team2_info = team2_info
        options = [
            discord.SelectOption(label=player, description="Team 1") for player in team1_info
        ] + [
            discord.SelectOption(label=player, description="Team 2") for player in team2_info
        ]
        super().__init__(placeholder="Choose a player to correct", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_player = self.values[0]
        self.view.clear_items()  # Clear previous items in the view
        self.view.add_item(StatCorrectionSelect(selected_player, self.team1_info, self.team2_info))
        await interaction.response.edit_message(content=f"You selected {selected_player}. What needs correction?", view=self.view)

class ConfirmationView(View):
    def __init__(self, user_id, team1_info, team2_info):
        super().__init__(timeout=180)
        self.user_id = user_id
        self.team1_info = team1_info
        self.team2_info = team2_info
        self.add_item(PlayerSelect(team1_info, team2_info))

    @discord.ui.button(label="Done", style=ButtonStyle.green, custom_id="confirm_done")
    async def confirm_done(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Corrections are complete. Thank you!", ephemeral=True)
        correction_completed_event.set()
        

async def confirm_stats(user_id, team1_info, team2_info):
    user = await bot.fetch_user(user_id)
    if user:
        dm_channel = await user.create_dm()
        view = ConfirmationView(user_id, team1_info, team2_info)
        await dm_channel.send("Please review the stats and make corrections as needed.", view=view)
        await correction_completed_event.wait()  # Wait until the corrections are confirmed as done
        correction_completed_event.clear()  # Reset the event for future use


# obtain correction from user mid-pipeline
async def prompt_correction(user_id, extracted_name):
    user = await bot.fetch_user(user_id)
    if user:
        dm_channel = await user.create_dm()
        message = (f"OCR extracted the name '{extracted_name}'. "
                   "Please reply with the correct name.")
        await dm_channel.send(message)

@bot.command(name='upload', help='Fetch a screenshot from users and provide an access code.')
async def upload(ctx):
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

