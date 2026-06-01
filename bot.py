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
# READY
# =========================
@bot.event
async def on_ready():
    print(f"🔴 UNITY ONLINE: {bot.user}")
    await bot.tree.sync()

# =========================
# LOGS BASE
# =========================
def log(guild, text):
    channel = discord.utils.get(guild.text_channels, name="📋・logs")
    if channel:
        return channel.send(text)

# =========================
# WELCOME / GOODBYE
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
# VERIFY SYSTEM
# =========================
class VerifyView(discord.ui.View):

    @discord.ui.button(label="Verifica", emoji="🔐", style=discord.ButtonStyle.danger)
    async def verify(self, interaction, button):

        role = discord.utils.get(interaction.guild.roles, name="Membro")

        if not role:
            return await interaction.response.send_message("❌ ruolo mancante", ephemeral=True)

        await interaction.user.add_roles(role)

        await interaction.response.send_message("🔐 verificato", ephemeral=True)

@bot.tree.command(name="verifypanel")
async def verifypanel(interaction):

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
async def annunci(interaction, titolo: str, messaggio: str):

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
async def ban(interaction, member: discord.Member, reason="no reason"):
    await member.ban(reason=reason)
    await interaction.response.send_message("🔨 bannato")

@bot.tree.command(name="kick")
async def kick(interaction, member: discord.Member, reason="no reason"):
    await member.kick(reason=reason)
    await interaction.response.send_message("👢 kickato")

@bot.tree.command(name="clear")
async def clear(interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message("🧹 pulito", ephemeral=True)

# =========================
# WARN SYSTEM
# =========================
@bot.tree.command(name="warn")
async def warn(interaction, member: discord.Member, reason="no reason"):

    warns = load_warns()
    uid = str(member.id)

    warns.setdefault(uid, []).append(reason)
    save_warns(warns)

    await interaction.response.send_message("⚠️ warn dato")

@bot.tree.command(name="warns")
async def warns(interaction, member: discord.Member):

    warns = load_warns().get(str(member.id), [])

    await interaction.response.send_message("\n".join(warns) if warns else "nessun warn")

# =========================
# ANTI SPAM
# =========================
@bot.event
async def on_message(message):

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
# ANTI RAID
# =========================
@bot.event
async def on_member_join(member):

    global raid_mode

    if raid_mode:
        await member.kick(reason="anti raid")

# =========================
# TICKET SYSTEM
# =========================
class TicketView(discord.ui.View):

    @discord.ui.button(label="Apri Ticket", emoji="🎫", style=discord.ButtonStyle.danger)
    async def open(self, interaction, button):

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
            title="🔴 TICKET UNITY",
            description=f"{user.mention}",
            color=discord.Color.red()
        )

        await channel.send(embed=embed, view=TicketControl())

        await interaction.response.send_message(f"🎫 {channel.mention}", ephemeral=True)

class TicketControl(discord.ui.View):

    @discord.ui.button(label="Claim", emoji="👑", style=discord.ButtonStyle.success)
    async def claim(self, interaction, button):

        role = discord.utils.get(interaction.guild.roles, name=STAFF_ROLE)

        if role not in interaction.user.roles:
            return await interaction.response.send_message("❌ solo staff", ephemeral=True)

        await interaction.channel.send(f"👑 claim {interaction.user.mention}")

    @discord.ui.button(label="Chiudi", emoji="🔒", style=discord.ButtonStyle.danger)
    async def close(self, interaction, button):

        await interaction.response.send_message("🔴 chiuso", ephemeral=True)
        await interaction.channel.delete()

@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction):

    embed = discord.Embed(
        title="🔴 UNITY TICKETS",
        color=discord.Color.red()
    )

    embed.set_image(url=BANNER)

    await interaction.response.send_message(embed=embed, view=TicketView())

# =========================
# ADMIN DASHBOARD
# =========================
class AdminView(discord.ui.View):

    @discord.ui.button(label="Raid ON/OFF", style=discord.ButtonStyle.danger)
    async def raid(self, interaction, button):

        global raid_mode
        raid_mode = not raid_mode

        await interaction.response.send_message(f"🚨 raid {raid_mode}", ephemeral=True)

@bot.tree.command(name="dashboard")
async def dashboard(interaction):

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