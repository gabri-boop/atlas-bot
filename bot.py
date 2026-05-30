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
# TICKET COUNTER
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
    try:
        await bot.tree.sync()
    except Exception as e:
        print(e)

# =========================
# WELCOME (NON MODIFICATO COME RICHIESTO)
# =========================
@bot.event
async def on_member_join(member):

    log = get_log_channel(member.guild, "📋・ᴍᴇᴍʙᴇʀ-ʟᴏɢꜱ")
    if log:
        await log.send(f"📥 {member} è entrato")

    welcome = discord.utils.get(member.guild.text_channels, name="👋・welcome")

    if welcome:
        embed = discord.Embed(
            title="🎉 BENVENUTO IN ATLAS COMMUNITY",
            description=(
                f"👋 Ciao {member.mention}\n\n"
                "📜 Leggi il regolamento\n"
                "🎫 Usa il ticket system\n\n"
                "🔥 Buona permanenza!"
            ),
            color=discord.Color.from_rgb(0, 90, 200)
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

    goodbye = discord.utils.get(member.guild.text_channels, name="💔・goodbye")

    if goodbye:
        embed = discord.Embed(
            title="👋 USCITA DAL SERVER",
            description=f"💔 {member.name} ha lasciato ATLAS COMMUNITY",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await goodbye.send(embed=embed)

# =========================
# MESSAGE LOG
# =========================
@bot.event
async def on_message_delete(message):

    if not message.guild or message.author.bot:
        return

    log = get_log_channel(message.guild, "📝・ᴍᴇꜱꜱᴀɢᴇ-ʟᴏɢꜱ")

    if log:
        embed = discord.Embed(
            title="🗑️ MESSAGGIO ELIMINATO",
            description=f"{message.author.mention}: {message.content}",
            color=discord.Color.orange()
        )
        await log.send(embed=embed)

# =========================
# MOD COMMANDS
# =========================
@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Nessun motivo"):
    await member.ban(reason=reason)
    await interaction.response.send_message("⛔ bannato")

@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Nessun motivo"):
    await member.kick(reason=reason)
    await interaction.response.send_message("👢 kickato")

@bot.tree.command(name="clear")
async def clear(interaction: discord.Interaction, amount: int):

    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ No permessi", ephemeral=True)

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message("🧹 pulito", ephemeral=True)

# =========================
# USER INFO
# =========================
@bot.tree.command(name="userinfo")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):

    member = member or interaction.user

    embed = discord.Embed(title="👤 USER INFO", color=discord.Color.blue())
    embed.add_field(name="Nome", value=member.name, inline=False)
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.set_thumbnail(url=member.display_avatar.url)

    await interaction.response.send_message(embed=embed)

# =========================
# AVATAR
# =========================
@bot.tree.command(name="avatar")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):

    member = member or interaction.user

    embed = discord.Embed(title="🖼️ Avatar")
    embed.set_image(url=member.display_avatar.url)

    await interaction.response.send_message(embed=embed)

# =========================
# TICKET SYSTEM
# =========================
class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Chiudi", style=discord.ButtonStyle.red, emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.channel.delete()

async def create_ticket(interaction: discord.Interaction, category: str):

    global ticket_counter

    ticket_counter += 1
    save_counter(ticket_counter)

    ticket_id = str(ticket_counter).zfill(4)

    cat = discord.utils.get(interaction.guild.categories, name="🎫 tickets")
    if not cat:
        cat = await interaction.guild.create_category("🎫 tickets")

    channel = await interaction.guild.create_text_channel(
        name=f"{category}-{ticket_id}",
        category=cat
    )

    await channel.set_permissions(interaction.guild.default_role, view_channel=False)
    await channel.set_permissions(interaction.user, view_channel=True, send_messages=True)

    embed = discord.Embed(
        title=f"🎫 TICKET #{ticket_id}",
        description=f"Categoria: {category.upper()}",
        color=discord.Color.from_rgb(0, 90, 255)
    )

    await channel.send(embed=embed, view=CloseView())

    await interaction.response.send_message(f"Creato {channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):

    @discord.ui.button(label="OWNER", style=discord.ButtonStyle.danger, emoji="👑")
    async def owner(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "owner")

    @discord.ui.button(label="STAFF", style=discord.ButtonStyle.primary, emoji="🛡️")
    async def staff(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "staff")

    @discord.ui.button(label="VALLEY", style=discord.ButtonStyle.success, emoji="🏝️")
    async def valley(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "valley")

@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎫 ATLAS COMMUNITY SUPPORT",
        description="Apri un ticket con i bottoni qui sotto",
        color=discord.Color.from_rgb(0, 90, 255)
    )

    await interaction.response.send_message(embed=embed, view=TicketView())

# =========================
# RUN BOT
# =========================
bot.run(TOKEN)