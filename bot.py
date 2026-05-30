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
# WELCOME
# =========================
@bot.event
async def on_member_join(member):

    log = get_log_channel(member.guild, "📋・ᴍᴇᴍʙᴇʀ-ʟᴏɢꜱ")
    if log:
        await log.send(f"📥 {member} è entrato")

    welcome = discord.utils.get(member.guild.text_channels, name="👋・welcome")

    if welcome:
        embed = discord.Embed(
            title="✨ BENVENUTO IN ATLAS COMMUNITY",
            description=f"👋 {member.mention}\n\n📜 Leggi il regolamento\n🎫 Usa /ticketpanel\n🔥 Buon divertimento!",
            color=discord.Color.from_rgb(0, 90, 255)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1482844068009738434/1510275949847908462/ChatGPT_Image_30_mag_2026_13_21_58.png")

        await welcome.send(embed=embed)

# =========================
# GOODBYE
# =========================
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
            title="🗑️ MESSAGGIO ELIMINATO",
            description=f"**Utente:** {message.author.mention}\n**Canale:** {message.channel.mention}\n**Contenuto:** {message.content}",
            color=discord.Color.orange()
        )
        await log.send(embed=embed)

@bot.event
async def on_message_edit(before, after):

    if not before.guild or before.author.bot:
        return

    if before.content == after.content:
        return

    log = get_log_channel(before.guild, "📝・ᴍᴇꜱꜱᴀɢᴇ-ʟᴏɢꜱ")

    if log:
        embed = discord.Embed(
            title="✏️ MESSAGGIO MODIFICATO",
            description=f"**Prima:** {before.content}\n**Dopo:** {after.content}",
            color=discord.Color.blue()
        )
        embed.set_author(name=str(before.author))
        await log.send(embed=embed)

# =========================
# MOD LOGS
# =========================
@bot.event
async def on_member_ban(guild, user):

    log = get_log_channel(guild, "🔨・ᴍᴏᴅ-ʟᴏɢꜱ")

    if log:
        await log.send(f"🔨 {user} bannato")

# =========================
# MOD COMMANDS FIXED
# =========================
@bot.tree.command(name="ban")
async def ban(interaction, member: discord.Member, reason: str = "Nessun motivo"):

    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ No permessi", ephemeral=True)

    await member.ban(reason=reason)
    await interaction.response.send_message(f"⛔ {member} bannato")

@bot.tree.command(name="kick")
async def kick(interaction, member: discord.Member, reason: str = "Nessun motivo"):

    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ No permessi", ephemeral=True)

    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 kickato")

@bot.tree.command(name="clear")
async def clear(interaction, amount: int):

    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ No permessi", ephemeral=True)

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 eliminati {amount}", ephemeral=True)

# =========================
# TICKET CLOSE BUTTON FIX
# =========================
class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Chiudi Ticket", style=discord.ButtonStyle.red, emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()

# =========================
# CREATE TICKET FIX
# =========================
async def create_ticket(interaction, category):

    global ticket_counter

    ticket_counter += 1
    save_counter(ticket_counter)

    ticket_id = str(ticket_counter).zfill(4)

    guild = interaction.guild
    user = interaction.user

    cat = discord.utils.get(guild.categories, name="🎫 tickets")
    if not cat:
        cat = await guild.create_category("🎫 tickets")

    channel = await guild.create_text_channel(
        name=f"{category}-{ticket_id}",
        category=cat
    )

    await channel.set_permissions(guild.default_role, view_channel=False)
    await channel.set_permissions(user, view_channel=True, send_messages=True)

    embed = discord.Embed(
        title=f"🎫 TICKET #{ticket_id}",
        description=f"Categoria: {category.upper()}\nStaff ti risponderà presto.",
        color=discord.Color.from_rgb(0, 90, 255)
    )

    await channel.send(embed=embed, view=CloseView())

    await interaction.response.send_message(f"Ticket creato: {channel.mention}", ephemeral=True)

# =========================
# TICKET PANEL FIX
# =========================
class TicketView(discord.ui.View):

    @discord.ui.button(label="OWNER", style=discord.ButtonStyle.danger, emoji="👑")
    async def owner(self, interaction, button):
        await create_ticket(interaction, "owner")

    @discord.ui.button(label="STAFF", style=discord.ButtonStyle.primary, emoji="🛡️")
    async def staff(self, interaction, button):
        await create_ticket(interaction, "staff")

    @discord.ui.button(label="VALLEY", style=discord.ButtonStyle.success, emoji="🏝️")
    async def valley(self, interaction, button):
        await create_ticket(interaction, "valley")

    @discord.ui.button(label="SUPPORTO", style=discord.ButtonStyle.secondary, emoji="🎮")
    async def supporto(self, interaction, button):
        await create_ticket(interaction, "supporto")

    @discord.ui.button(label="BUG", style=discord.ButtonStyle.secondary, emoji="🐛")
    async def bug(self, interaction, button):
        await create_ticket(interaction, "bug")

@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction):

    embed = discord.Embed(
        title="⚡ ATLAS COMMUNITY SUPPORT",
        description="Seleziona una categoria per aprire un ticket",
        color=discord.Color.from_rgb(0, 90, 255)
    )

    embed.set_image(url="https://cdn.discordapp.com/attachments/1482844068009738434/1510275949847908462/ChatGPT_Image_30_mag_2026_13_21_58.png")

    await interaction.response.send_message(embed=embed, view=TicketView())

# =========================
# RUN
# =========================
bot.run(TOKEN)