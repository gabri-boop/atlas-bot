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
# BANNER UNITY
# =========================
BANNER_URL = "https://cdn.discordapp.com/attachments/1482844068009738434/1511074300755574975/ChatGPT_Image_1_giu_2026_20_28_18.png?ex=6a1f211b&is=6a1dcf9b&hm=b8d82f9c3a92dd86129fe18b2cac6e71820ef87131e7bf64398d3fa380877625&"

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    print(f"🤖 Online come UNITY BOT ({bot.user})")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands sincronizzati: {len(synced)}")
    except Exception as e:
        print(e)

# =========================
# VERIFY SYSTEM
# =========================
class VerifyView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verificami", emoji="✅", style=discord.ButtonStyle.success)
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):

        role = discord.utils.get(interaction.guild.roles, name="Membro")

        if role is None:
            return await interaction.response.send_message(
                "❌ Ruolo 'Membro' non trovato.",
                ephemeral=True
            )

        if role in interaction.user.roles:
            return await interaction.response.send_message(
                "⚠️ Sei già verificato.",
                ephemeral=True
            )

        await interaction.user.add_roles(role)

        await interaction.response.send_message(
            "✅ Verifica completata! Benvenuto in UNITY.",
            ephemeral=True
        )

@bot.tree.command(name="verifypanel")
async def verifypanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🔒 VERIFICA UNITY",
        description=(
            "👋 Benvenuto!\n\n"
            "Per accedere al server devi verificarti.\n\n"
            "Premi il bottone qui sotto 👇\n\n"
            "🎫 Accesso completo ai canali\n"
            "⚠️ Sistema automatico"
        ),
        color=discord.Color.from_rgb(0, 90, 200)
    )

    embed.set_image(url=BANNER_URL)

    await interaction.response.send_message(
        embed=embed,
        view=VerifyView()
    )

# =========================
# ANNUNCI SYSTEM
# =========================
@bot.tree.command(name="annunci", description="Invia un annuncio stile webhook con banner")
async def annunci(
    interaction: discord.Interaction,
    titolo: str,
    messaggio: str
):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            "❌ Non hai i permessi per usare questo comando.",
            ephemeral=True
        )

    embed = discord.Embed(
        title=f"📢 {titolo}",
        description=messaggio,
        color=discord.Color.from_rgb(0, 90, 200)
    )

    embed.set_author(
        name=interaction.user.name,
        icon_url=interaction.user.display_avatar.url
    )

    embed.set_image(url=BANNER_URL)

    embed.set_footer(text="UNITY ANNOUNCEMENTS SYSTEM")

    await interaction.channel.send(embed=embed)

    await interaction.response.send_message(
        "✅ Annuncio inviato con successo!",
        ephemeral=True
    )

# =========================
# TICKET SYSTEM (SEMPLIFICATO)
# =========================
class TicketView(discord.ui.View):

    @discord.ui.button(label="Supporto", style=discord.ButtonStyle.primary, emoji="🎫")
    async def supporto(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        user = interaction.user

        category = discord.utils.get(guild.categories, name="🎫 TICKETS")

        if not category:
            category = await guild.create_category("🎫 TICKETS")

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category
        )

        await channel.set_permissions(guild.default_role, read_messages=False)
        await channel.set_permissions(user, read_messages=True, send_messages=True)

        embed = discord.Embed(
            title="🎫 UNITY TICKET",
            description="Supporto aperto, attendi lo staff.",
            color=discord.Color.from_rgb(0, 90, 200)
        )

        await channel.send(embed=embed)

        await interaction.response.send_message(
            f"Ticket creato: {channel.mention}",
            ephemeral=True
        )

@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎫 UNITY",
        description="Apri un ticket per assistenza 💬",
        color=discord.Color.from_rgb(0, 90, 200)
    )

    embed.set_image(url=BANNER_URL)

    await interaction.response.send_message(embed=embed, view=TicketView())

# =========================
# RUN
# =========================
bot.run(TOKEN)import discord
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
# UTILS
# =========================
def get_log_channel(guild, name):
    return discord.utils.get(guild.text_channels, name=name)

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    print(f"🤖 Online come UNITY BOT ({bot.user})")
    try:
        synced = await bot.tree.sync()
        print(f"Slash commands sincronizzati: {len(synced)}")
    except Exception as e:
        print(e)

# =========================
# WELCOME
# =========================
@bot.event
async def on_member_join(member):

    channel = get_log_channel(member.guild, "📋・ᴍᴇᴍʙᴇʀ-ʟᴏɢꜱ")
    if channel:
        embed = discord.Embed(
            title="📥 NUOVO MEMBRO",
            description=f"{member.mention} è entrato in UNITY",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

    welcome = discord.utils.get(member.guild.text_channels, name="👋・ᴡᴇʟᴄᴏᴍᴇ")

    if welcome:
        embed = discord.Embed(
            title="🎉 BENVENUTO IN UNITY",
            description=(
                f"👋 Ciao {member.mention}\n\n"
                "📜 Leggi il regolamento\n"
                "🎫 Usa il ticket system\n\n"
                "🔥 Buona permanenza in UNITY!"
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

    channel = get_log_channel(member.guild, "📋・ᴍᴇᴍʙᴇʀ-ʟᴏɢꜱ")
    if channel:
        embed = discord.Embed(
            title="📤 MEMBRO USCITO",
            description=f"**{member}** ha lasciato UNITY",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)

    goodbye = discord.utils.get(member.guild.text_channels, name="💔・ɢᴏᴏᴅʙʏᴇ")

    if goodbye:
        embed = discord.Embed(
            title="👋 USCITA DAL SERVER",
            description=f"💔 {member.name} ha lasciato UNITY",
            color=discord.Color.from_rgb(10, 30, 80)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await goodbye.send(embed=embed)

# =========================
# VERIFY SYSTEM
# =========================
class VerifyView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verificami", emoji="✅", style=discord.ButtonStyle.success)
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):

        role = discord.utils.get(interaction.guild.roles, name="Membro")

        if role is None:
            return await interaction.response.send_message(
                "❌ Ruolo 'Membro' non trovato.",
                ephemeral=True
            )

        if role in interaction.user.roles:
            return await interaction.response.send_message(
                "⚠️ Sei già verificato.",
                ephemeral=True
            )

        await interaction.user.add_roles(role)

        await interaction.response.send_message(
            "✅ Verifica completata! Benvenuto in UNITY.",
            ephemeral=True
        )

@bot.tree.command(name="verifypanel")
async def verifypanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🔒 VERIFICA UNITY",
        description=(
            "👋 Benvenuto!\n\n"
            "Per accedere al server devi verificarti.\n\n"
            "Premi il bottone qui sotto 👇\n\n"
            "🎫 Accesso completo ai canali\n"
            "⚠️ Sistema automatico"
        ),
        color=discord.Color.from_rgb(0, 90, 200)
    )

    embed.set_image(
        url="https://cdn.discordapp.com/attachments/1482844068009738434/1510275949847908462/ChatGPT_Image_30_mag_2026_13_21_58.png"
    )

    await interaction.response.send_message(
        embed=embed,
        view=VerifyView()
    )

# =========================
# ANNUNCI SYSTEM
# =========================
@bot.tree.command(name="annunci", description="Invia un annuncio stile webhook con banner")
async def annunci(
    interaction: discord.Interaction,
    titolo: str,
    messaggio: str
):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            "❌ Non hai i permessi per usare questo comando.",
            ephemeral=True
        )

    banner_url = "https://cdn.discordapp.com/attachments/1482844068009738434/1510275949847908462/ChatGPT_Image_30_mag_2026_13_21_58.png"

    embed = discord.Embed(
        title=f"📢 {titolo}",
        description=messaggio,
        color=discord.Color.from_rgb(0, 90, 200)
    )

    embed.set_author(
        name=interaction.user.name,
        icon_url=interaction.user.display_avatar.url
    )

    embed.set_image(url=banner_url)

    embed.set_footer(text="UNITY ANNOUNCEMENTS SYSTEM")

    await interaction.channel.send(embed=embed)

    await interaction.response.send_message(
        "✅ Annuncio inviato con successo!",
        ephemeral=True
    )

# =========================
# RUN
# =========================
bot.run(TOKEN)
