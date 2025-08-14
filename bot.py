import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import sys

# .env yükle
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN is None:
    raise ValueError("DISCORD_TOKEN bulunamadı! .env dosyasını kontrol et.")

# Bot ayarları
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Uyarı veritabanı
warnings = {}

# Küfür listesi dosyadan oku
def load_profanity():
    if os.path.exists("profanity.txt"):
        with open("profanity.txt", "r", encoding="utf-8") as f:
            return [line.strip().lower() for line in f if line.strip()]
    return []

bad_words = load_profanity()

# DM mesajları
warning_messages = [
    """Merhaba,
Gönderdiğiniz içerik platform kurallarımıza aykırıdır. Lütfen topluluk kurallarını tekrar gözden geçirin ve bu tür paylaşımlardan kaçının.

⚠ Uyarı Politikası:

Uyarı: Bilgilendirme

Uyarı: Son uyarı

Uyarı: 1 gün süreyle timeout""",

    """Dikkat!

Topluluğumuzda küfür etmek ve hakaret etmek kesinlikle kabul edilemez. Bu davranış, kuralları çiğnemekle kalmıyor, tamamen seviyesizliktir.

⚠ Bu son şansın!

Bir kez daha böyle bir hareket yaparsan, anında ve süresiz engellenirsin.

Gerekirse seni tamamen platformdan atarız, geri dönüşün de olmaz.

Burada herkes birbirine saygı gösterecek. Eğer bu sana ağır geliyorsa, çıkış kapısı tam karşında.""",

    """⚠️ DİKKAT: SON UYARI DA AŞILDI ⚠️

Daha önce yapılan uyarılar dikkate alınmamıştır. Bu grup, belirlenen kurallar çerçevesinde düzenli ve saygılı bir şekilde kullanılmak zorundadır. Kuralların ihlali devam ettiği için artık tolerans gösterilmeyecektir.

Kurallara uymamak, hem grup düzenini bozmak hem de diğer üyelerin haklarını ihlal etmek anlamına gelir. Bu, gruptan çıkarılmanız için son aşamadır.

Bu mesajdan sonra bir ihlal daha yaşanırsa, hiçbir ek uyarı yapılmadan gruptan çıkarılacaksınız.

Grubun ciddiyetini anlamayan, saygı göstermeyen kimse burada yer alamaz. Tekrarı halinde daha uzun süreli uzaklaştırma uygulanabilir. Topluluğun düzenini korumak için anlayışınız için teşekkür ederiz."""
]

@bot.event
async def on_ready():
    print(f"✅ Bot giriş yaptı: {bot.user}")

# Ping komutu
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")

# Küfür filtresi
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content.lower()
    if any(word in content for word in bad_words):
        await message.delete()
        await add_warning(message.channel, message.author, "Küfür/Hakaret")

    await bot.process_commands(message)

# Uyarı ekleme fonksiyonu
async def add_warning(channel, member, reason):
    user_id = str(member.id)
    if user_id not in warnings:
        warnings[user_id] = []

    warnings[user_id].append(reason)
    warn_count = len(warnings[user_id])

    # DM ile uyarı gönder
    try:
        if warn_count <= 3:
            await member.send(warning_messages[warn_count-1])
        else:
            await member.send("❌ Çok geç! Kuralları tekrar ihlal ettiğin için uzaklaştırıldın.")
    except:
        await channel.send(f"⚠ {member.mention} DM kapalı olduğu için mesaj gönderilemedi.")

    # 4. uyarıda kick
    if warn_count >= 4:
        try:
            await member.kick(reason="Çok fazla kural ihlali")
            await channel.send(f"❌ {member.mention} kuralları defalarca ihlal ettiği için uzaklaştırıldı.")
        except discord.Forbidden:
            await channel.send("❌ Kick yetkim yok!")

# Komut: !warnings
@bot.command()
async def warnings_list(ctx, member: discord.Member = None):
    member = member or ctx.author
    user_id = str(member.id)
    count = len(warnings.get(user_id, []))
    await ctx.send(f"⚠ {member.mention} uyarı sayısı: {count}")

# Komut: !resetwarn (admin)
@bot.command()
@commands.has_permissions(administrator=True)
async def resetwarn(ctx, member: discord.Member):
    user_id = str(member.id)
    warnings[user_id] = []
    await ctx.send(f"✅ {member.mention} uyarıları sıfırlandı.")

# Restart komutu (sahip)
@bot.command()
@commands.is_owner()
async def restart(ctx):
    await ctx.send("🔄 Bot yeniden başlatılıyor...")
    await bot.close()
    os.execv(sys.executable, ['python'] + sys.argv)

bot.run(TOKEN)
