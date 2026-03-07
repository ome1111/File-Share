# (©) Persistent Bottom Menu System
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import StopPropagation

from bot import Bot
from database.database import user_data

# ==========================================
# 🎛️ 1. WALLET BUTTON
# ==========================================
# group=-1 ব্যবহার করা হয়েছে যাতে Link Generator এর আগে এটি কাজ করে
@Bot.on_message(filters.regex("My Wallet") & filters.private, group=-1)
async def menu_wallet(client: Client, message: Message):
    user_id = message.from_user.id
    user = user_data.find_one({"_id": user_id}) or {}

    balance = round(user.get('balance', 0.0), 3)
    views = user.get('views', 0)
    referrals = user.get('referrals', 0)

    text = f"""
💳 **Yᴏᴜʀ Eᴀʀɴɪɴɢ Wᴀʟʟᴇᴛ**

👤 **Uꜱᴇʀ:** {message.from_user.mention}
👀 **Tᴏᴛᴀʟ Vɪᴇᴡꜱ:** `{views}`
💰 **Tᴏᴛᴀʟ Bᴀʟᴀɴᴄᴇ:** `৳ {balance}`
👥 **Tᴏᴛᴀʟ Rᴇғᴇʀʀᴀʟꜱ:** `{referrals}`

*Sʜᴀʀᴇ ʏᴏᴜʀ ғɪʟᴇ ʟɪɴᴋꜱ ᴏʀ ɪɴᴠɪᴛᴇ ғʀɪᴇɴᴅꜱ ᴛᴏ ᴇᴀʀɴ ᴍᴏʀᴇ!*
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("💸 Withdraw Money", callback_data="withdraw_money"),
         InlineKeyboardButton("📜 History", callback_data="withdraw_history")]
    ])
    await message.reply_text(text, reply_markup=reply_markup)
    raise StopPropagation # মেসেজটি এখানেই থামিয়ে দেবে, শর্টলিংক বানাতে যাবে না

# ==========================================
# 🏆 2. LEADERBOARD BUTTON
# ==========================================
@Bot.on_message(filters.regex("Leaderboard") & filters.private, group=-1)
async def menu_leaderboard(client: Client, message: Message):
    # ডাটাবেস থেকে সবচেয়ে বেশি ইনকাম করা ১০ জনকে বের করা
    top_users = user_data.find().sort("balance", -1).limit(10)
    
    text = "🏆 **Tᴏᴘ 10 Eᴀʀɴᴇʀꜱ Lᴇᴀᴅᴇʀʙᴏᴀʀᴅ**\n\n"
    medals = ["🥇", "🥈", "🥉", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅"]
    
    count = 0
    for user in top_users:
        balance = round(user.get('balance', 0.0), 3)
        views = user.get('views', 0)
        text += f"{medals[count]} **UID:** `{user['_id']}` ➔ ৳ `{balance}` ({views} views)\n"
        count += 1

    if count == 0:
        text += "No earners found yet!"

    await message.reply_text(text)
    raise StopPropagation

# ==========================================
# 🔗 3. REFERRAL LINK BUTTON
# ==========================================
@Bot.on_message(filters.regex("Referral Link") & filters.private, group=-1)
async def menu_referral(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = client.me.username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    text = f"""
🔗 **Yᴏᴜʀ Rᴇғᴇʀʀᴀʟ Lɪɴᴋ**

`{ref_link}`

🎁 **Bᴏɴᴜs:**
Invite your friends using this link. When they join and earn money, you will get a **5% lifetime commission** from their earnings automatically!
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={ref_link}")]
    ])
    await message.reply_text(text, reply_markup=reply_markup, disable_web_page_preview=True)
    raise StopPropagation

# ==========================================
# 👤 4. PROFILE BUTTON
# ==========================================
@Bot.on_message(filters.regex("My Profile") & filters.private, group=-1)
async def menu_profile(client: Client, message: Message):
    user_id = message.from_user.id
    user = user_data.find_one({"_id": user_id})
    
    if not user:
        await message.reply_text("❌ Profile not found! Please send /start first.")
        raise StopPropagation

    join_date = user.get("join_date")
    date_str = join_date.strftime("%Y-%m-%d") if hasattr(join_date, 'strftime') else "Unknown"
    warnings = user.get("warnings", 0)
    status = "🔴 BANNED" if user.get("is_banned") else "🟢 ACTIVE"

    text = f"""
👤 **Uꜱᴇʀ Pʀᴏғɪʟᴇ Sᴛᴀᴛᴜꜱ**

**Nᴀᴍᴇ:** {message.from_user.first_name}
**UID:** `{user_id}`
**Sᴛᴀᴛᴜꜱ:** {status}
**Wᴀʀɴɪɴɢꜱ:** {warnings}/3
**Jᴏɪɴ Dᴀᴛᴇ:** `{date_str}`
**Lᴀɴɢᴜᴀɢᴇ:** `{user.get('lang', 'en').upper()}`
"""
    await message.reply_text(text)
    raise StopPropagation

# ==========================================
# ⚙️ 5. SETTINGS BUTTON
# ==========================================
@Bot.on_message(filters.regex("Settings") & filters.private, group=-1)
async def menu_settings(client: Client, message: Message):
    text = "⚙️ **Yᴏᴜʀ Sᴇᴛᴛɪɴɢꜱ Mᴇɴ জ্ঞ**\n\n_Select your preferred language below:_"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"),
         InlineKeyboardButton("🇧🇩 বাংলা", callback_data="set_lang_bn"),
         InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="set_lang_hi")]
    ])
    await message.reply_text(text, reply_markup=reply_markup)
    raise StopPropagation

# ==========================================
# ❓ 6. HELP BUTTON
# ==========================================
@Bot.on_message(filters.regex("Help & Info") & filters.private, group=-1)
async def menu_help(client: Client, message: Message):
    text = """
❓ **Hᴏᴡ ᴛᴏ Uꜱᴇ ᴛʜɪꜱ Bᴏᴛ:**

1️⃣ Send or forward any file/video to me.
2️⃣ I will generate a unique **Earning Link**.
3️⃣ Share it with friends or channels.
4️⃣ When someone opens the link, you get views & money! 💸

_Need more help? Contact Admin._
"""
    await message.reply_text(text)
    raise StopPropagation
