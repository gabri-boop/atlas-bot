import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json

# =========================
# TOKEN
# =========================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("❌ DISCORD_TOKEN non trovato")

# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# COUNTER TICKET
# =========================
COUNTER_FILE = "ticket_counter.json"

def load_counter():
    if not os.path.exists(COUNTER_FILE):
        return 0
    with open(COUNTER_FILE, "r") as f:
        return json.load(f).get("count", 0)

def save_counter(value):
    with open(COUNTER_FILE, "w") as f:
        json.dump({"count": value}, f)

ticket_counter = load_counter()

# =========================
# LOG UTILS
# =========================
def get_log_channel(guild, name):
    return discord.utils.get(guild.text_channels, name=name)

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    print(f"🤖 Online come {bot.user}")
    await bot.tree.sync()

# =========================
# WELCOME / GOODBYE
# =========================
@bot.event
async def on_member_join(member):

    log = get_log_channel(member.guild, "📋・ᴍᴇᴍʙᴇʀ-ʟᴏɢꜱ")
    if log:
        await log.send(f"📥 {member} è entrato")

    welcome = discord.utils.get(member.guild.text_channels, name="👋・welcome")

    if welcome:
        embed = discord.Embed(
            title="✨ BENVENUTO IN ATLAS",
            description=f"👋 {member.mention}\nUsa /ticketpanel",
            color=discord.Color.from_rgb(0, 90, 255)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await welcome.send(embed=embed)

@bot.event
async def on_member_remove(member):

    log = get_log_channel(member.guild, "📋・ᴍᴇᴍʙᴇʀ-ʟᴏɢꜱ")
    if log:
        await log.send(f"📤 {member} è uscito")

# =========================
# MESSAGE LOGS
# =========================
@bot.event
async def on_message_delete(message):

    if not message.guild or message.author.bot:
        return

    log = get_log_channel(message.guild, "📝・ᴍᴇꜱꜱᴀɢᴇ-ʟᴏɢꜱ")

    if log:
        embed = discord.Embed(
            title="🗑️ DELETE",
            description=f"{message.author.mention}: {message.content}",
            color=discord.Color.orange()
        )
        await log.send(embed=embed)

# =========================
# MOD LOGS
# =========================
@bot.event
async def on_member_ban(guild, user):

    log = get_log_channel(guild, "🔨・ᴍᴏᴅ-ʟᴏɢꜱ")

    if log:
        await log.send(f"🔨 BAN: {user}")

# =========================
# MOD COMMANDS
# =========================
@bot.tree.command(name="ban")
async def ban(interaction, member: discord.Member, reason: str = "Nessun motivo"):

    await member.ban(reason=reason)
    await interaction.response.send_message(f"⛔ {member} bannato")

@bot.tree.command(name="kick")
async def kick(interaction, member: discord.Member, reason: str = "Nessun motivo"):

    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 {member} kickato")

@bot.tree.command(name="clear")
async def clear(interaction, amount: int):

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message("🧹 Pulito", ephemeral=True)

# =========================
# 🔥 NUOVI COMANDI MOD
# =========================

@bot.tree.command(name="warn")
async def warn(interaction, member: discord.Member, reason: str = "Nessun motivo"):
    await interaction.response.send_message(f"⚠️ {member.mention} warn: {reason}")

@bot.tree.command(name="userinfo")
async def userinfo(interaction, member: discord.Member = None):

    member = member or interaction.user

    embed = discord.Embed(title="👤 USER INFO", color=discord.Color.blue())
    embed.add_field(name="Nome", value=member.name)
    embed.add_field(name="ID", value=member.id)
    embed.set_thumbnail(url=member.display_avatar.url)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="mute")
async def mute(interaction, member: discord.Member, minutes: int, reason: str = "Nessun motivo"):

    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("❌ No permessi", ephemeral=True)

    duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
    await member.timeout(duration, reason=reason)

    await interaction.response.send_message(f"🔇 {member} mutato")

@bot.tree.command(name="unmute")
async def unmute(interaction, member: discord.Member):

    if not interaction.user.guild_permissions.moderate_members:
        return await interaction.response.send_message("❌ No permessi", ephemeral=True)

    await member.timeout(None)
    await interaction.response.send_message(f"🔊 {member} smutato")

@bot.tree.command(name="lock")
async def lock(interaction):

    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = False

    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)

    await interaction.response.send_message("🔒 lock")

@bot.tree.command(name="unlock")
async def unlock(interaction):

    overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
    overwrite.send_messages = True

    await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)

    await interaction.response.send_message("🔓 unlock")

@bot.tree.command(name="purge")
async def purge(interaction, amount: int):

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message("🧹 pulito", ephemeral=True)

@bot.tree.command(name="avatar")
async def avatar(interaction, member: discord.Member = None):

    member = member or interaction.user

    embed = discord.Embed()
    embed.set_image(url=member.display_avatar.url)

    await interaction.response.send_message(embed=embed)

# =========================
# TICKET SYSTEM
# =========================
class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="Chiudi", style=discord.ButtonStyle.red)
    async def close(self, interaction, button):
        await interaction.channel.delete()

async def create_ticket(interaction, category):

    global ticket_counter

    ticket_counter += 1
    save_counter(ticket_counter)

    tid = str(ticket_counter).zfill(4)

    cat = discord.utils.get(interaction.guild.categories, name="🎫 tickets")
    if not cat:
        cat = await interaction.guild.create_category("🎫 tickets")

    ch = await interaction.guild.create_text_channel(f"{category}-{tid}", category=cat)

    await ch.set_permissions(interaction.guild.default_role, view_channel=False)
    await ch.set_permissions(interaction.user, view_channel=True, send_messages=True)

    embed = discord.Embed(
        title=f"🎫 TICKET #{tid}",
        description=f"Categoria: {category}",
        color=discord.Color.from_rgb(0, 90, 255)
    )

    await ch.send(embed=embed, view=CloseView())

    await interaction.response.send_message(f"Creato {ch.mention}", ephemeral=True)

class TicketView(discord.ui.View):

    @discord.ui.button(label="OWNER", style=discord.ButtonStyle.danger)
    async def owner(self, i, b):
        await create_ticket(i, "owner")

    @discord.ui.button(label="STAFF", style=discord.ButtonStyle.primary)
    async def staff(self, i, b):
        await create_ticket(i, "staff")

    @discord.ui.button(label="VALLEY", style=discord.ButtonStyle.success)
    async def valley(self, i, b):
        await create_ticket(i, "valley")

@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction):

    embed = discord.Embed(
        title="🎫 ATLAS SUPPORT",
        description="Apri un ticket",
        color=discord.Color.from_rgb(0, 90, 255)
    )

    await interaction.response.send_message(embed=embed, view=TicketView())

# =========================
# RUN
# =========================
bot.run(TOKEN)
