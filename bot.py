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
    print("❌ TOKEN NON TROVATO")
    exit()

# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# COUNTER PERSISTENTE
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
# READY
# =========================
@bot.event
async def on_ready():
    print(f"🤖 Online come {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands sincronizzati: {len(synced)}")
    except Exception as e:
        print("Sync error:", e)

# =========================
# MOD COMMANDS
# =========================
@bot.tree.command(name="ping")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

@bot.tree.command(name="ban")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Nessun motivo"):
    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message("❌ No permessi", ephemeral=True)

    await member.ban(reason=reason)
    await interaction.response.send_message(f"⛔ {member} bannato")

@bot.tree.command(name="kick")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Nessun motivo"):
    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message("❌ No permessi", ephemeral=True)

    await member.kick(reason=reason)
    await interaction.response.send_message(f"👢 {member} kickato")

@bot.tree.command(name="clear")
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ No permessi", ephemeral=True)

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 Eliminati {amount} messaggi", ephemeral=True)

# =========================
# CLOSE TICKET
# =========================
class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Chiudi Ticket", style=discord.ButtonStyle.red, emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 Chiusura ticket...")
        await interaction.channel.delete()

# =========================
# CREA TICKET PRO
# =========================
async def create_ticket(interaction: discord.Interaction, category: str):

    global ticket_counter

    ticket_counter += 1
    save_counter(ticket_counter)

    ticket_id = str(ticket_counter).zfill(4)

    guild = interaction.guild
    user = interaction.user

    # categoria automatica
    cat = discord.utils.get(guild.categories, name="🎫 tickets")
    if cat is None:
        cat = await guild.create_category("🎫 tickets")

    channel = await guild.create_text_channel(
        name=f"{category}-{ticket_id}",
        category=cat
    )

    bot_member = guild.get_member(bot.user.id)

    await channel.set_permissions(guild.default_role, read_messages=False)
    await channel.set_permissions(user, read_messages=True, send_messages=True)

    if bot_member:
        await channel.set_permissions(bot_member, read_messages=True, send_messages=True)

    embed = discord.Embed(
        title=f"🎫 ATLAS COMMUNITY — TICKET #{ticket_id}",
        description=(
            f"Categoria: **{category.upper()}**\n\n"
            "Attendi risposta dallo staff.\n"
            "Mantieni un comportamento corretto."
        ),
        color=discord.Color.from_rgb(20, 30, 55)
    )

    embed.set_footer(text=f"ATLAS SUPPORT SYSTEM • Ticket #{ticket_id}")

    await channel.send(embed=embed, view=CloseView())

    await interaction.response.send_message(
        f"✅ Ticket creato: {channel.mention} (`#{ticket_id}`)",
        ephemeral=True
    )

# =========================
# TICKET PANEL (BOTTONI)
# =========================
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="OWNER", style=discord.ButtonStyle.danger, emoji="👑", row=0)
    async def owner(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "owner")

    @discord.ui.button(label="STAFF", style=discord.ButtonStyle.primary, emoji="🛡️", row=0)
    async def staff(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "staff")

    @discord.ui.button(label="VALLEY", style=discord.ButtonStyle.success, emoji="🏝️", row=0)
    async def valley(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "valley")

    @discord.ui.button(label="SUPPORTO", style=discord.ButtonStyle.secondary, emoji="🎮", row=1)
    async def supporto(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "supporto")

    @discord.ui.button(label="BUG REPORT", style=discord.ButtonStyle.secondary, emoji="🐛", row=1)
    async def bug(self, interaction: discord.Interaction, button: discord.ui.Button):
        await create_ticket(interaction, "bug")

# =========================
# PANEL EMBED RP + BRANDING
# =========================
@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎫 ATLAS COMMUNITY — SUPPORT SYSTEM",
        description=(
            "Sistema ufficiale di assistenza.\n\n"
            "Seleziona una categoria per aprire un ticket.\n"
            "Lo staff risponderà il prima possibile.\n\n"
            "⚠️ Uso improprio = sanzione"
        ),
        color=discord.Color.from_rgb(15, 18, 25)
    )

    embed.set_author(
        name="ATLAS COMMUNITY SUPPORT",
        icon_url="https://cdn.discordapp.com/attachments/1482844068009738434/1510275950234042528/ChatGPT_Image_30_mag_2026_13_23_39.png"
    )

    embed.set_image(
        url="https://cdn.discordapp.com/attachments/1482844068009738434/1510275949847908462/ChatGPT_Image_30_mag_2026_13_21_58.png"
    )

    embed.set_footer(text="ATLAS COMMUNITY • Support System")

    await interaction.response.send_message(embed=embed, view=TicketView())

# =========================
# RUN
# =========================
bot.run(TOKEN)