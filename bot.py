import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import json
import asyncio

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
# ANTI RAID
# =========================
join_count = {}

# =========================
# UTILS
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
# =========================
# 👋 WELCOME (COME ORIGINALE - NON MODIFICATO)
# =========================
# =========================
@bot.event
async def on_member_join(member):

    # ANTI RAID
    gid = member.guild.id

    if gid not in join_count:
        join_count[gid] = 0

    join_count[gid] += 1

    if join_count[gid] >= 5:
        log = get_log_channel(member.guild, "🔨・ᴍᴏᴅ-ʟᴏɢꜱ")
        if log:
            await log.send("🚨 POSSIBILE RAID IN CORSO!")
        join_count[gid] = 0

    # MEMBER LOG
    channel = get_log_channel(member.guild, "📋・ᴍᴇᴍʙᴇʀ-ʟᴏɢꜱ")
    if channel:
        embed = discord.Embed(
            title="📥 NUOVO MEMBRO",
            description=f"{member.mention} è entrato nel server",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

    # WELCOME CHAT (IDENTICO COME PRIMA)
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

    # DM WELCOME
    try:
        embed = discord.Embed(
            title="🎉 Benvenuto in ATLAS",
            description="Usa /ticketpanel per aiuto",
            color=discord.Color.blue()
        )
        await member.send(embed=embed)
    except:
        pass

# =========================
# GOODBYE
# =========================
@bot.event
async def on_member_remove(member):

    channel = get_log_channel(member.guild, "📋・ᴍᴇᴍʙᴇʀ-ʟᴏɢꜱ")
    if channel:
        await channel.send(f"📤 {member} è uscito")

    goodbye = discord.utils.get(member.guild.text_channels, name="💔・goodbye")

    if goodbye:
        embed = discord.Embed(
            title="👋 USCITA DAL SERVER",
            description=f"💔 {member.name} ha lasciato ATLAS",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await goodbye.send(embed=embed)

# =========================
# LOG MESSAGGI
# =========================
@bot.event
async def on_message_delete(message):

    if not message.guild or message.author.bot:
        return

    log = get_log_channel(message.guild, "📝・ᴍᴇꜱꜱᴀɢᴇ-ʟᴏɢꜱ")

    if log:
        embed = discord.Embed(
            title="🗑️ DELETE",
            description=f"{message.author}: {message.content}",
            color=discord.Color.orange()
        )
        await log.send(embed=embed)

# =========================
# MOD LOG
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
async def ban(interaction, member: discord.Member, reason="Nessun motivo"):
    await member.ban(reason=reason)
    await interaction.response.send_message("⛔ bannato")

@bot.tree.command(name="kick")
async def kick(interaction, member: discord.Member, reason="Nessun motivo"):
    await member.kick(reason=reason)
    await interaction.response.send_message("👢 kickato")

@bot.tree.command(name="clear")
async def clear(interaction, amount: int):
    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message("🧹 pulito", ephemeral=True)

# =========================
# NUOVI COMANDI
# =========================
@bot.tree.command(name="userinfo")
async def userinfo(interaction, member: discord.Member = None):

    member = member or interaction.user

    embed = discord.Embed(title="👤 USER INFO", color=discord.Color.blue())
    embed.add_field(name="Nome", value=member.name)
    embed.add_field(name="ID", value=member.id)
    embed.set_thumbnail(url=member.display_avatar.url)

    await interaction.response.send_message(embed=embed)

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
        title="🎫 ATLAS COMMUNITY",
        description="Apri un ticket",
        color=discord.Color.from_rgb(0, 90, 255)
    )

    await interaction.response.send_message(embed=embed, view=TicketView())

# =========================
# RUN
# =========================
bot.run(TOKEN)
