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
# BANNER
# =========================
BANNER_URL = "https://cdn.discordapp.com/attachments/1482844068009738434/1511074300755574975/ChatGPT_Image_1_giu_2026_20_28_18.png"

# =========================
# READY
# =========================
@bot.event
async def on_ready():
    print(f"🤖 UNITY BOT ONLINE ({bot.user})")
    try:
        await bot.tree.sync()
        print("Slash commands sincronizzati")
    except Exception as e:
        print(e)

# =========================
# VERIFY SYSTEM
# =========================
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verificami", style=discord.ButtonStyle.success, emoji="✅")
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
            "✅ Verifica completata!",
            ephemeral=True
        )

@bot.tree.command(name="verifypanel")
async def verifypanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🔒 UNITY VERIFICA",
        description="Premi il bottone per verificarti.",
        color=discord.Color.from_rgb(0, 90, 200)
    )

    embed.set_image(url=BANNER_URL)

    await interaction.response.send_message(embed=embed, view=VerifyView())

# =========================
# ANNUNCI
# =========================
@bot.tree.command(name="annunci")
async def annunci(interaction: discord.Interaction, titolo: str, messaggio: str):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            "❌ No permessi",
            ephemeral=True
        )

    embed = discord.Embed(
        title=f"📢 {titolo}",
        description=messaggio,
        color=discord.Color.blue()
    )

    embed.set_image(url=BANNER_URL)

    await interaction.channel.send(embed=embed)

    await interaction.response.send_message(
        "✅ Annuncio inviato",
        ephemeral=True
    )

# =========================
# TICKET (SEMPLICE E STABILE)
# =========================
class TicketView(discord.ui.View):

    @discord.ui.button(label="Apri Ticket", style=discord.ButtonStyle.primary, emoji="🎫")
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):

        guild = interaction.guild
        user = interaction.user

        category = discord.utils.get(guild.categories, name="TICKETS")
        if category is None:
            category = await guild.create_category("TICKETS")

        channel = await guild.create_text_channel(
            name=f"ticket-{user.name}",
            category=category
        )

        await channel.set_permissions(guild.default_role, read_messages=False)
        await channel.set_permissions(user, read_messages=True, send_messages=True)

        await channel.send(f"🎫 Ticket aperto da {user.mention}")

        await interaction.response.send_message(
            f"Ticket creato: {channel.mention}",
            ephemeral=True
        )

@bot.tree.command(name="ticketpanel")
async def ticketpanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎫 UNITY TICKET",
        description="Premi per aprire un ticket",
        color=discord.Color.blue()
    )

    embed.set_image(url=BANNER_URL)

    await interaction.response.send_message(embed=embed, view=TicketView())

# =========================
# RUN
# =========================
bot.run(TOKEN)