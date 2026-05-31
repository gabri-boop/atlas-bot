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
# UTILS LOG CHANNEL
# =========================
def get_log_channel(guild, name):
    return discord.utils.get(guild.text_channels, name=name)

# =========================
# READY
# =========================
@bot.event
async def on_ready(bot.loop.create_task(update_server_status())):
    print(f"🤖 Online come {bot.user}")
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
            description=f"{member.mention} è entrato nel server",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

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

    channel = get_log_channel(member.guild, "📋・ᴍᴇᴍʙᴇʀ-ʟᴏɢꜱ")
    if channel:
        embed = discord.Embed(
            title="📤 MEMBRO USCITO",
            description=f"**{member}** ha lasciato il server",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)

    goodbye = discord.utils.get(member.guild.text_channels, name="💔・goodbye")

    if goodbye:
        embed = discord.Embed(
            title="👋 USCITA DAL SERVER",
            description=f"💔 {member.name} ha lasciato ATLAS COMMUNITY",
            color=discord.Color.from_rgb(10, 30, 80)
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await goodbye.send(embed=embed)

# =========================
# MESSAGE LOGS
# =========================
@bot.event
async def on_message_delete(message):

    if not message.guild or message.author.bot:
        return

    channel = get_log_channel(message.guild, "📝・ᴍᴇꜱꜱᴀɢᴇ-ʟᴏɢꜱ")

    if channel:
        embed = discord.Embed(
            title="🗑️ MESSAGGIO ELIMINATO",
            color=discord.Color.orange()
        )
        embed.add_field(name="Utente", value=message.author.mention, inline=False)
        embed.add_field(name="Canale", value=message.channel.mention, inline=False)
        embed.add_field(name="Contenuto", value=message.content or "vuoto", inline=False)
        await channel.send(embed=embed)

@bot.event
async def on_message_edit(before, after):

    if not before.guild or before.author.bot:
        return

    if before.content == after.content:
        return

    channel = get_log_channel(before.guild, "📝・ᴍᴇꜱꜱᴀɢᴇ-ʟᴏɢꜱ")

    if channel:
        embed = discord.Embed(
            title="✏️ MESSAGGIO MODIFICATO",
            color=discord.Color.blue()
        )
        embed.add_field(name="Utente", value=before.author.mention, inline=False)
        embed.add_field(name="Prima", value=before.content[:1024] or "vuoto", inline=False)
        embed.add_field(name="Dopo", value=after.content[:1024] or "vuoto", inline=False)
        await channel.send(embed=embed)

# =========================
# MOD LOGS
# =========================
@bot.event
async def on_member_ban(guild, user):

    channel = get_log_channel(guild, "🔨・ᴍᴏᴅ-ʟᴏɢꜱ")

    if channel:
        embed = discord.Embed(
            title="🔨 BAN",
            description=f"{user.mention} bannato",
            color=discord.Color.red()
        )
        await channel.send(embed=embed)

@bot.event
async def on_member_unban(guild, user):

    channel = get_log_channel(guild, "🔨・ᴍᴏᴅ-ʟᴏɢꜱ")

    if channel:
        embed = discord.Embed(
            title="🔓 UNBAN",
            description=f"{user.mention} sbannato",
            color=discord.Color.green()
        )
        await channel.send(embed=embed)

# =========================
# TEST COMMANDS
# =========================
@bot.tree.command(name="benvenuto")
async def benvenuto(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎉 TEST WELCOME",
        description=f"👋 {interaction.user.mention}",
        color=discord.Color.from_rgb(0, 90, 200)
    )

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="addio")
async def addio(interaction: discord.Interaction):

    embed = discord.Embed(
        title="👋 TEST GOODBYE",
        description=f"💔 {interaction.user.name}",
        color=discord.Color.red()
    )

    await interaction.response.send_message(embed=embed)

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
    await interaction.response.send_message(f"👢 kickato")

@bot.tree.command(name="clear")
async def clear(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        return await interaction.response.send_message("❌ No permessi", ephemeral=True)

    await interaction.channel.purge(limit=amount)
    await interaction.response.send_message(f"🧹 eliminati {amount}")

# =========================
# TICKET SYSTEM
# =========================
class CloseView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Chiudi Ticket", style=discord.ButtonStyle.red, emoji="🔒")
    async def close(self, interaction, button):
        await interaction.channel.delete()

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

    await channel.set_permissions(guild.default_role, read_messages=False)
    await channel.set_permissions(user, read_messages=True, send_messages=True)

    embed = discord.Embed(
        title=f"🎫 ATLAS TICKET #{ticket_id}",
        description=f"Categoria: {category.upper()}",
        color=discord.Color.from_rgb(0, 90, 200)
    )

    await channel.send(embed=embed, view=CloseView())

    await interaction.response.send_message(f"Ticket creato: {channel.mention}", ephemeral=True)

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
async def ticketpanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🎫 ATLAS COMMUNITY",
        description="Apri un ticket 💬🔥",
        color=discord.Color.from_rgb(0, 90, 200)
    )

    embed.set_image(url="https://cdn.discordapp.com/attachments/1482844068009738434/1510275949847908462/ChatGPT_Image_30_mag_2026_13_21_58.png")

    await interaction.response.send_message(embed=embed, view=TicketView()) 
    
# =========================
# VERIFY SYSTEM
# =========================

class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Verificami",
        emoji="✅",
        style=discord.ButtonStyle.success
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):

        role = discord.utils.get(
            interaction.guild.roles,
            name="Membro"
        )

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
            "✅ Verifica completata! Benvenuto in ATLAS COMMUNITY.",
            ephemeral=True
        )


@bot.tree.command(name="verifypanel")
async def verifypanel(interaction: discord.Interaction):

    embed = discord.Embed(
        title="🔒 VERIFICA ATLAS COMMUNITY",
        description=(
            "👋 Benvenuto!\n\n"
            "Per accedere al server devi verificarti.\n\n"
            "✅ Premi il bottone qui sotto\n"
            "🎫 Accesso completo ai canali\n\n"
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
    async def update_server_status():

    await bot.wait_until_ready()

    while not bot.is_closed():

        for guild in bot.guilds:

            channel = discord.utils.get(guild.text_channels, name="📊・ꜱᴇʀᴠᴇʀ-ꜱᴛᴀᴛᴜꜱ")

            if not channel:
                continue

            total_members = guild.member_count

            online_members = len([
                m for m in guild.members
                if str(m.status) != "offline" and not m.bot
            ])

            boosters = guild.premium_subscription_count

            embed = discord.Embed(
                title="📊 SERVER STATUS LIVE",
                color=discord.Color.from_rgb(0, 90, 200)
            )

            embed.add_field(name="👥 Membri Totali", value=str(total_members), inline=True)
            embed.add_field(name="🟢 Online", value=str(online_members), inline=True)
            embed.add_field(name="🚀 Boost", value=str(boosters), inline=True)

            embed.set_footer(text="Aggiornamento automatico ogni 60s")

            await channel.purge(limit=1)
            await channel.send(embed=embed)

        await asyncio.sleep(60)

# =========================
# RUN
# =========================
bot.run(TOKEN)
