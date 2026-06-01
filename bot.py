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
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# CONFIG
# =========================
BANNER_URL = "https://cdn.discordapp.com/attachments/1482844068009738434/1511074300755574975/ChatGPT_Image_1_giu_2026_20_28_18.png"

STAFF_ROLE_NAME = "🎫 Support"
TICKET_CATEGORY = "🎫 TICKETS"

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    print(f"🤖 UNITY ONLINE ({bot.user})")
    await bot.tree.sync()

# =========================
# VERIFY SYSTEM
# =========================
class VerifyView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verifica", emoji="🔐", style=discord.ButtonStyle.danger)
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):

        role = discord.utils.get(interaction.guild.roles, name="Membro")

        if not role:
            return await interaction.response.send_message("❌ Ruolo Membro non trovato", ephemeral=True)

        if role in interaction.user.roles:
            return await interaction.response.send_message("⚠️ Già verificato", ephemeral=True)

        await interaction.user.add_roles(role)

        await interaction.response.send_message("🔐 Verifica completata", ephemeral=True)

@bot.tree.command(name="verifypanel")
async def verifypanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🔐 UNITY VERIFICA",
        description="Premi il bottone per verificarti",
        color=discord.Color.red()
    )

    embed.set_image(url=BANNER_URL)

    await interaction.response.send_message(embed=embed, view=VerifyView())

# =========================
# ANNUNCI
# =========================
@bot.tree.command(name="annunci")
async def annunci(interaction: discord.Interaction, titolo: str, messaggio: str):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message("❌ No permessi", ephemeral=True)

    embed = discord.Embed(
        title=f"🔴 {titolo}",
        description=messaggio,
        color=discord.Color.red()
    )

    embed.set_image(url=BANNER_URL)

    await interaction.channel.send(embed=embed)

    await interaction.response.send_message("🔴 Inviato", ephemeral=True)

# =========================
# TICKET SYSTEM
# =========================
class TicketControl(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim", emoji="👑", style=discord.ButtonStyle.success)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):

        staff_role = discord.utils.get(interaction.guild.roles, name=STAFF_ROLE_NAME)

        if staff_role not in interaction.user.roles:
            return await interaction.response.send_message(
                "❌ Solo 🎫 Support può fare claim",
                ephemeral=True
            )

        await interaction.channel.send(f"👑 Ticket preso da {interaction.user.mention}")

        await interaction.response.send_message("🔴 Claim effettuato", ephemeral=True)

    @discord.ui.button(label="Chiudi", emoji="🔒", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

        await interaction.response.send_message("🔴 Ticket chiuso", ephemeral=True)
        await interaction.channel.delete()

class TicketOpen(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

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

        await channel.send(embed=embed, view=TicketControl())

        await interaction.response.send_message(
            f"🎫 Ticket creato: {channel.mention}",
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

    await interaction.response.send_message(embed=embed, view=TicketOpen())

# =========================
# RUN
# =========================
bot.run(TOKEN)