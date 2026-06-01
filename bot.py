import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

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

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# CONFIG
# =========================
BANNER_URL = "https://cdn.discordapp.com/attachments/1482844068009738434/1511074300755574975/ChatGPT_Image_1_giu_2026_20_28_18.png"
STAFF_ROLE_NAME = "Staff"
TICKET_CATEGORY = "🎫 TICKETS"

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    print(f"🤖 UNITY BOT ONLINE ({bot.user})")
    await bot.tree.sync()

# =========================
# VERIFY SYSTEM (RED)
# =========================
class VerifyView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verificami", emoji="🔴", style=discord.ButtonStyle.danger)
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
            "🔴 Verifica completata! Benvenuto in UNITY.",
            ephemeral=True
        )

@bot.tree.command(name="verifypanel")
async def verifypanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🔴 VERIFICA UNITY",
        description=(
            "👋 Benvenuto!\n\n"
            "Premi il bottone per verificarti\n\n"
            "🔴 Accesso ai canali"
        ),
        color=discord.Color.red()
    )

    embed.set_image(url=BANNER_URL)

    await interaction.response.send_message(embed=embed, view=VerifyView())

# =========================
# ANNUNCI (RED)
# =========================
@bot.tree.command(name="annunci")
async def annunci(interaction: discord.Interaction, titolo: str, messaggio: str):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            "❌ No permessi",
            ephemeral=True
        )

    embed = discord.Embed(
        title=f"🔴 {titolo}",
        description=messaggio,
        color=discord.Color.red()
    )

    embed.set_image(url=BANNER_URL)

    await interaction.channel.send(embed=embed)

    await interaction.response.send_message(
        "🔴 Annuncio inviato",
        ephemeral=True
    )

# =========================
# TICKET SYSTEM (ADVANCED RED)
# =========================
class TicketControlView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.success, emoji="👑")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):

        staff_role = discord.utils.get(interaction.guild.roles, name=STAFF_ROLE_NAME)

        if staff_role not in interaction.user.roles:
            return await interaction.response.send_message(
                "❌ Solo staff",
                ephemeral=True
            )

        await interaction.channel.send(f"👑 Ticket preso da {interaction.user.mention}")
        await interaction.response.send_message("🔴 Claim effettuato", ephemeral=True)

    @discord.ui.button(label="Chiudi", style=discord.ButtonStyle.danger, emoji="🔒")
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message("🔴 Ticket chiuso", ephemeral=True)
        await interaction.channel.delete()


class TicketOpenView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Apri Ticket", style=discord.ButtonStyle.danger, emoji="🎫")
    async def open(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        user = interaction.user

        category = discord.utils.get(guild.categories, name=TICKET_CATEGORY)
        if category is None:
            category = await guild.create_category(TICKET_CATEGORY)

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}".lower(),
            category=category
        )

        staff_role = discord.utils.get(guild.roles, name=STAFF_ROLE_NAME)

        await channel.set_permissions(guild.default_role, read_messages=False)
        await channel.set_permissions(user, read_messages=True, send_messages=True)

        if staff_role:
            await channel.set_permissions(staff_role, read_messages=True, send_messages=True)

        embed = discord.Embed(
            title="🔴 TICKET UNITY",
            description=f"Supporto per {user.mention}",
            color=discord.Color.red()
        )

        await channel.send(embed=embed, view=TicketControlView())

        await interaction.response.send_message(
            f"🔴 Ticket creato: {channel.mention}",
            ephemeral=True
        )

@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🔴 UNITY TICKETS",
        description="Apri un ticket per supporto",
        color=discord.Color.red()
    )

    embed.set_image(url=BANNER_URL)

    await interaction.response.send_message(embed=embed, view=TicketOpenView())

# =========================
# RUN
# =========================
bot.run(TOKEN)