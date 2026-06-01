import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json
import time

# =========================
# TOKEN
# =========================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN mancante")

# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# CONFIG
# =========================
BANNER = "https://cdn.discordapp.com/attachments/1482844068009738434/1511074300755574975/ChatGPT_Image_1_giu_2026_20_28_18.png"

STAFF_ROLE = "🎫 Support"
TICKET_CATEGORY = "🎫 TICKETS"

WARN_FILE = "warns.json"

raid_mode = False
spam_cache = {}

# =========================
# WARN SYSTEM
# =========================
def load_warns():
    if not os.path.exists(WARN_FILE):
        return {}
    with open(WARN_FILE, "r") as f:
        return json.load(f)

def save_warns(data):
    with open(WARN_FILE, "w") as f:
        json.dump(data, f, indent=4)

# =========================
# LOG SYSTEM FIXED
# =========================
async def log(guild, text):
    channel = discord.utils.get(guild.text_channels, name="📋・logs")
    if channel:
        await channel.send(text)

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    print(f"🔴 UNITY ONLINE: {bot.user}")
    await bot.tree.sync()

# =========================
# JOIN / LEAVE (FIXED)
# =========================
@bot.event
async def on_member_join(member):

    global raid_mode

    if raid_mode:
        await member.kick(reason="Anti Raid")
        return

    await log(member.guild, f"🟢 JOIN {member}")

    welcome = discord.utils.get(member.guild.text_channels, name="👋・welcome")

    if welcome:
        embed = discord.Embed(
            title="🔴 UNITY",
            description=f"Benvenuto {member.mention}",
            color=discord.Color.red()
        )
        embed.set_image(url=BANNER)
        await welcome.send(embed=embed)

@bot.event
async def on_member_remove(member):
    await log(member.guild, f"🔴 LEAVE {member}")

# =========================
# VERIFY
# =========================
class VerifyView(discord.ui.View):

    @discord.ui.button(label="Verifica", emoji="🔐", style=discord.ButtonStyle.danger)
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):

        role = discord.utils.get(interaction.guild.roles, name="Membro")

        if not role:
            return await interaction.response.send_message("❌ ruolo mancante", ephemeral=True)

        await interaction.user.add_roles(role)

        await interaction.response.send_message("🔐 verificato", ephemeral=True)

@bot.tree.command(name="verifypanel")
async def verifypanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🔐 UNITY VERIFY",
        color=discord.Color.red()
    )

    embed.set_image(url=BANNER)

    await interaction.response.send_message(embed=embed, view=VerifyView())

# =========================
# ANNUNCI
# =========================
@bot.tree.command(name="annunci")
async def annunci(interaction: discord.Interaction, titolo: str, messaggio: str):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ no permessi", ephemeral=True)

    embed = discord.Embed(
        title=f"🔴 {titolo}",
        description=messaggio,
        color=discord.Color.red()
    )

    embed.set_image(url=BANNER)

    await interaction.channel.send(embed=embed)

    await interaction.response.send_message("✔ inviato", ephemeral=True)

# =========================
# MODERAZIONE
# =========================
@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "no reason"):
    await member.ban(reason=reason)
    await interaction.response.send_message("🔨 bannato")

@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "no reason"):
    await member.kick(reason=reason)
    await interaction.response.send_message("👢 kickato")

@bot.tree.command(name="clear")
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message("🧹 pulito", ephemeral=True)

# =========================
# WARN SYSTEM
# =========================
@bot.tree.command(name="warn")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str = "no reason"):

    warns = load_warns()
    uid = str(member.id)

    warns.setdefault(uid, []).append(reason)
    save_warns(warns)

    await interaction.response.send_message("⚠️ warn dato")

@bot.tree.command(name="warns")
async def warns(interaction: discord.Interaction, member: discord.Member):

    warns = load_warns().get(str(member.id), [])

    await interaction.response.send_message("\n".join(warns) if warns else "nessun warn")

# =========================
# ANTI SPAM (FIXED)
# =========================
@bot.event
async def on_message(message: discord.Message):

    global spam_cache

    if message.author.bot:
        return

    uid = message.author.id
    now = time.time()

    spam_cache.setdefault(uid, []).append(now)

    spam_cache[uid] = [t for t in spam_cache[uid] if now - t < 5]

    if len(spam_cache[uid]) > 5:
        await message.channel.send(f"⚠️ spam {message.author.mention}")

    await bot.process_commands(message)

# =========================
# TICKET SYSTEM (FIXED)
# =========================
class TicketView(discord.ui.View):

    @discord.ui.button(label="Apri Ticket", emoji="🎫", style=discord.ButtonStyle.danger)
    async def open(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        user = interaction.user

        category = discord.utils.get(guild.categories, name=TICKET_CATEGORY)
        if not category:
            category = await guild.create_category(TICKET_CATEGORY)

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}".lower(),
            category=category
        )

        staff = discord.utils.get(guild.roles, name=STAFF_ROLE)

        await channel.set_permissions(guild.default_role, read_messages=False)
        await channel.set_permissions(user, read_messages=True, send_messages=True)

        if staff:
            await channel.set_permissions(staff, read_messages=True, send_messages=True)

        embed = discord.Embed(
            title="🔴 UNITY TICKET",
            description=f"{user.mention}",
            color=discord.Color.red()
        )

        await channel.send(embed=embed)

        await interaction.response.send_message(f"🎫 {channel.mention}", ephemeral=True)

@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🔴 UNITY TICKETS",
        color=discord.Color.red()
    )

    embed.set_image(url=BANNER)

    await interaction.response.send_message(embed=embed, view=TicketView())

# =========================
# DASHBOARD ADMIN
# =========================
class AdminView(discord.ui.View):

    @discord.ui.button(label="Raid ON/OFF", style=discord.ButtonStyle.danger)
    async def raid(self, interaction: discord.Interaction, button: discord.ui.Button):

        global raid_mode
        raid_mode = not raid_mode

        await interaction.response.send_message(f"🚨 raid {raid_mode}", ephemeral=True)

@bot.tree.command(name="dashboard")
async def dashboard(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ no permessi", ephemeral=True)

    embed = discord.Embed(
        title="⚙️ UNITY DASHBOARD",
        color=discord.Color.red()
    )

    embed.set_image(url=BANNER)

    await interaction.response.send_message(embed=embed, view=AdminView(), ephemeral=True)

# =========================
# RUN
# =========================
bot.run(TOKEN)