import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import logging

# =========================
# CONFIG
# =========================
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN mancante")

BANNER = "https://cdn.discordapp.com/attachments/1482844068009738434/1511074300755574975/ChatGPT_Image_1_giu_2026_20_28_18.png"

MEMBER_ROLE_ID = 1511007478593355776

# =========================
# LOGGING
# =========================
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("UNITY")

# =========================
# INTENTS
# =========================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# =========================
# BOT
# =========================
class UnityBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        await self.tree.sync()
        log.info("Slash commands sincronizzati")

bot = UnityBot()

# =========================
# 💎 PREMIUM EMBED STYLE
# =========================
def premium_embed(title: str, desc: str, color=discord.Color.red()):
    e = discord.Embed(
        title=f"🌍 UNITY • {title}",
        description=desc,
        color=color
    )
    e.set_footer(
        text="UNITY • Secure System • Premium Experience",
        icon_url="https://cdn.discordapp.com/embed/avatars/0.png"
    )
    e.set_image(url=BANNER)
    return e

# =========================
# VERIFY VIEW (premium UI)
# =========================
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🔓 Sblocca Accesso",
        style=discord.ButtonStyle.success,
        custom_id="unity_verify"
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):

        role = interaction.guild.get_role(MEMBER_ROLE_ID)

        if not role:
            return await interaction.response.send_message(
                embed=premium_embed("Errore", "Ruolo Member non trovato nel sistema."),
                ephemeral=True
            )

        if role in interaction.user.roles:
            return await interaction.response.send_message(
                embed=premium_embed(
                    "Già verificato",
                    "Hai già accesso completo alla community."
                ),
                ephemeral=True
            )

        if not interaction.guild.me.guild_permissions.manage_roles:
            return await interaction.response.send_message(
                embed=premium_embed(
                    "Errore permessi",
                    "Non ho permesso di gestire i ruoli."
                ),
                ephemeral=True
            )

        if role >= interaction.guild.me.top_role:
            return await interaction.response.send_message(
                embed=premium_embed(
                    "Errore gerarchia",
                    "Sistema ruoli non configurato correttamente."
                ),
                ephemeral=True
            )

        try:
            await interaction.user.add_roles(role, reason="UNITY verification system")
        except discord.Forbidden:
            return await interaction.response.send_message(
                embed=premium_embed("Errore", "Impossibile assegnare il ruolo."),
                ephemeral=True
            )

        await interaction.response.send_message(
            embed=premium_embed(
                "Accesso Concesso",
                "Sei stato verificato con successo.\nBenvenuto in **UNITY**."
            ),
            ephemeral=True
        )

# =========================
# READY EVENT
# =========================
@bot.event
async def on_ready():
    log.info(f"UNITY ONLINE: {bot.user}")
    bot.add_view(VerifyView())

# =========================
# 💌 DM WELCOME (NEW PREMIUM FEATURE)
# =========================
@bot.event
async def on_member_join(member):

    # TRY DM USER
    try:
        dm = premium_embed(
            "Benvenuto su UNITY",
            "Sei appena entrato nella nostra community.\n\n"
            "🔓 Completa la verifica per accedere a tutte le sezioni\n"
            "📜 Rispetta le regole\n"
            "🚀 Buona permanenza!"
        )

        await member.send(embed=dm)

    except discord.Forbidden:
        log.warning(f"DM bloccati per {member}")

    # SERVER WELCOME CHANNEL
    channel = discord.utils.get(member.guild.text_channels, name="👋・welcome")
    if not channel:
        return

    embed = premium_embed(
        "NUOVO MEMBRO",
        f"👋 Benvenuto {member.mention}\n\n"
        "Completa la verifica per sbloccare il server.\n\n"
        f"👥 Membri totali: **{member.guild.member_count}**"
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    await channel.send(embed=embed)

# =========================
# GOODBYE
# =========================
@bot.event
async def on_member_remove(member):

    channel = discord.utils.get(member.guild.text_channels, name="👋・goodbye")
    if not channel:
        return

    embed = premium_embed(
        "UTENTE USCITO",
        f"**{member.name}** ha lasciato UNITY.\n\n"
        "Grazie per aver fatto parte della community."
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    await channel.send(embed=embed)

# =========================
# VERIFY PANEL
# =========================
@bot.tree.command(name="verifypanel", description="Invia pannello verifica premium")
@app_commands.checks.has_permissions(administrator=True)
async def verifypanel(interaction: discord.Interaction):

    embed = premium_embed(
        "VERIFICATION SYSTEM",
        "Per accedere alla community devi completare la verifica.\n\n"
        "🔓 Premi il pulsante qui sotto\n"
        "⚡ Accesso immediato dopo verifica"
    )

    await interaction.response.send_message(embed=embed, view=VerifyView())

# =========================
# ANNUNCI
# =========================
@bot.tree.command(name="annunci", description="Invia annuncio premium")
@app_commands.checks.has_permissions(administrator=True)
async def annunci(interaction: discord.Interaction, titolo: str, messaggio: str):

    embed = premium_embed(
        f"ANNUNCIO • {titolo}",
        f"📢 {messaggio}"
    )

    await interaction.channel.send(embed=embed)

    await interaction.response.send_message(
        "✅ Annuncio pubblicato con successo.",
        ephemeral=True
    )

# =========================
# BAN
# =========================
@bot.tree.command(name="ban", description="Banna utente")
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Nessun motivo"):

    await member.ban(reason=reason)

    await interaction.response.send_message(
        embed=premium_embed(
            "BAN ESEGUITO",
            f"🚫 {member.mention} è stato bannato\n\nMotivo: {reason}"
        )
    )

# =========================
# KICK
# =========================
@bot.tree.command(name="kick", description="Espelli utente")
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Nessun motivo"):

    await member.kick(reason=reason)

    await interaction.response.send_message(
        embed=premium_embed(
            "UTENTE ESPULSO",
            f"👢 {member.mention} è stato espulso\n\nMotivo: {reason}"
        )
    )

# =========================
# CLEAR
# =========================
@bot.tree.command(name="clear", description="Cancella messaggi")
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, amount: int):

    await interaction.response.defer(ephemeral=True)

    deleted = await interaction.channel.purge(limit=amount)

    await interaction.followup.send(
        embed=premium_embed(
            "PULIZIA CHAT",
            f"🧹 Eliminati **{len(deleted)}** messaggi."
        ),
        ephemeral=True
    )

# =========================
# RUN BOT
# =========================
bot.run(TOKEN)