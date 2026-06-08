import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# =========================
# CONFIG
# =========================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN mancante")

BANNER = "https://cdn.discordapp.com/attachments/1482844068009738434/1511074300755574975/ChatGPT_Image_1_giu_2026_20_28_18.png"

MEMBER_ROLE = "🌍 Member"

# =========================
# BOT
# =========================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# =========================
# VERIFY VIEW
# =========================
class VerifyView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Ottieni Accesso",
        emoji="🌍",
        style=discord.ButtonStyle.success,
        custom_id="unity_verify"
    )
    async def verify(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        role = discord.utils.get(
            interaction.guild.roles,
            name=MEMBER_ROLE
        )

        if not role:
            return await interaction.response.send_message(
                "❌ Ruolo 🌍 Member non trovato.",
                ephemeral=True
            )

        if role in interaction.user.roles:
            return await interaction.response.send_message(
                "✅ Sei già verificato.",
                ephemeral=True
            )

        await interaction.user.add_roles(role)

        await interaction.response.send_message(
            "✅ Verifica completata! Benvenuto su UNITY.",
            ephemeral=True
        )

# =========================
# READY
# =========================
@bot.event
async def on_ready():

    print(f"🔴 UNITY ONLINE: {bot.user}")

    bot.add_view(VerifyView())

    try:
        await bot.tree.sync()
        print("✅ Slash Commands sincronizzati")
    except Exception as e:
        print(e)

# =========================
# WELCOME
# =========================
@bot.event
async def on_member_join(member):

    channel = discord.utils.get(
        member.guild.text_channels,
        name="👋・welcome"
    )

    if not channel:
        return

    embed = discord.Embed(
        title="🌍 BENVENUTO SU UNITY",
        description=(
            f"Ciao {member.mention}!\n\n"
            "Benvenuto nella community ufficiale di UNITY.\n"
            "Leggi il regolamento e completa la verifica "
            "per ottenere l'accesso completo al server.\n\n"
            f"👥 Membri Totali: **{member.guild.member_count}**"
        ),
        color=discord.Color.red()
    )

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url=BANNER)

    await channel.send(embed=embed)

# =========================
# GOODBYE
# =========================
@bot.event
async def on_member_remove(member):

    channel = discord.utils.get(
        member.guild.text_channels,
        name="👋・goodbye"
    )

    if not channel:
        return

    embed = discord.Embed(
        title="👋 ARRIVEDERCI",
        description=(
            f"**{member.name}** ha lasciato il server.\n\n"
            "Grazie per aver fatto parte di UNITY.\n"
            "Ti auguriamo il meglio!"
        ),
        color=discord.Color.red()
    )

    embed.set_thumbnail(url=member.display_avatar.url)
    embed.set_image(url=BANNER)

    await channel.send(embed=embed)

# =========================
# VERIFY PANEL
# =========================
@bot.tree.command(
    name="verifypanel",
    description="Invia il pannello verifica"
)
async def verifypanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🌍 UNITY VERIFY",
        description=(
            "Benvenuto su UNITY!\n\n"
            "Premi il pulsante qui sotto per ottenere "
            "l'accesso completo al server."
        ),
        color=discord.Color.red()
    )

    embed.add_field(
        name="📜 Regolamento",
        value="Leggi il regolamento prima di verificarti.",
        inline=False
    )

    embed.add_field(
        name="🔓 Accesso",
        value="Riceverai il ruolo 🌍 Member.",
        inline=False
    )

    embed.set_image(url=BANNER)

    await interaction.response.send_message(
        embed=embed,
        view=VerifyView()
    )

# =========================
# ANNUNCI
# =========================
@bot.tree.command(
    name="annunci",
    description="Invia un annuncio"
)
async def annunci(
    interaction: discord.Interaction,
    titolo: str,
    messaggio: str
):

    if not interaction.user.guild_permissions.administrator:
        return await interaction.response.send_message(
            "❌ Non hai i permessi.",
            ephemeral=True
        )

    embed = discord.Embed(
        title=f"📢 {titolo}",
        description=messaggio,
        color=discord.Color.red()
    )

    embed.set_image(url=BANNER)

    await interaction.channel.send(embed=embed)

    await interaction.response.send_message(
        "✅ Annuncio inviato.",
        ephemeral=True
    )

# =========================
# BAN
# =========================
@bot.tree.command(
    name="ban",
    description="Banna un utente"
)
async def ban(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "Nessun motivo"
):

    if not interaction.user.guild_permissions.ban_members:
        return await interaction.response.send_message(
            "❌ Non hai i permessi.",
            ephemeral=True
        )

    await member.ban(reason=reason)

    await interaction.response.send_message(
        f"🔨 {member.mention} bannato.\nMotivo: {reason}"
    )

# =========================
# KICK
# =========================
@bot.tree.command(
    name="kick",
    description="Espelli un utente"
)
async def kick(
    interaction: discord.Interaction,
    member: discord.Member,
    reason: str = "Nessun motivo"
):

    if not interaction.user.guild_permissions.kick_members:
        return await interaction.response.send_message(
            "❌ Non hai i permessi.",
            ephemeral=True
        )

    await member.kick(reason=reason)

    await interaction.response.send_message(
        f"👢 {member.mention} espulso.\nMotivo: {reason}"
    )

# =========================
# CLEAR
# =========================
@bot.tree.command(
    name="clear",
    description="Cancella messaggi"
)
async def clear(
    interaction: discord.Interaction,
    amount: int
):

    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message(
            "❌ Non hai i permessi.",
            ephemeral=True
        )

    await interaction.response.defer(ephemeral=True)

    deleted = await interaction.channel.purge(limit=amount)

    await interaction.followup.send(
        f"🧹 Eliminati {len(deleted)} messaggi.",
        ephemeral=True
    )

# =========================
# RUN
# =========================
bot.run(TOKEN)
