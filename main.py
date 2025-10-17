import discord
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Load/save user data
def load_data():
    if os.path.exists('levels.json'):
        with open('levels.json', 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open('levels.json', 'w') as f:
        json.dump(data, f, indent=4)

user_data = load_data()

def get_xp_for_level(level):
    return level * 100

def update_nickname(member, level):
    try:
        if level > 100:
            new_nick = f"{member.name} 🔥 ∞"
        else:
            new_nick = f"{member.name} 🔥 {level}"
        
        if member.guild.me.top_role > member.top_role:
            return member.edit(nick=new_nick)
    except discord.Forbidden:
        print(f"Cannot update nickname for {member.name}")
    except Exception as e:
        print(f"Error: {e}")

@bot.event
async def on_ready():
    print(f'{bot.user} is online!')

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    user_id = str(message.author.id)
    guild_id = str(message.guild.id)
    
    if guild_id not in user_data:
        user_data[guild_id] = {}
    
    if user_id not in user_data[guild_id]:
        user_data[guild_id][user_id] = {"xp": 0, "level": 1}
    
    # Add XP per message (adjust as needed)
    user_data[guild_id][user_id]["xp"] += 10
    
    current_level = user_data[guild_id][user_id]["level"]
    current_xp = user_data[guild_id][user_id]["xp"]
    xp_needed = get_xp_for_level(current_level)
    
    if current_xp >= xp_needed and current_level < 101:
        user_data[guild_id][user_id]["level"] += 1
        user_data[guild_id][user_id]["xp"] = 0
        new_level = user_data[guild_id][user_id]["level"]
        
        await update_nickname(message.author, new_level)
        await message.channel.send(f"🎉 {message.author.mention} leveled up to **Level {new_level}**!")
    
    save_data(user_data)
    await bot.process_commands(message)

@bot.command()
async def rank(ctx):
    user_id = str(ctx.author.id)
    guild_id = str(ctx.guild.id)
    
    if guild_id in user_data and user_id in user_data[guild_id]:
        level = user_data[guild_id][user_id]["level"]
        xp = user_data[guild_id][user_id]["xp"]
        xp_needed = get_xp_for_level(level)
        
        embed = discord.Embed(title=f"{ctx.author.name}'s Rank", color=discord.Color.orange())
        embed.add_field(name="Level", value=f"🔥 {level if level <= 100 else '∞'}", inline=True)
        embed.add_field(name="XP", value=f"{xp}/{xp_needed}", inline=True)
        await ctx.send(embed=embed)
    else:
        await ctx.send("You haven't earned any XP yet!")

@bot.command()
@commands.has_permissions(administrator=True)
async def setlevel(ctx, member: discord.Member, level: int):
    user_id = str(member.id)
    guild_id = str(ctx.guild.id)
    
    if guild_id not in user_data:
        user_data[guild_id] = {}
    
    user_data[guild_id][user_id] = {"xp": 0, "level": level}
    save_data(user_data)
    
    await update_nickname(member, level)
    await ctx.send(f"Set {member.mention} to level {level}!")

bot.run('YOUR_BOT_TOKEN')
