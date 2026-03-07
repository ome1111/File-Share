# (©) Persistent Bottom Menu System
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from bot import Bot
from database.database import get_user_wallet, get_top_earners, get_user

# ==========================================
# 🎛️ 1. WALLET BUTTON
# ==========================================
@Bot.on_message(filters.regex("^💰 My Wallet$") & filters.private)
async def menu_wallet(client: Client, message: Message):
    user_id = message.from_user.id
    wallet = await get_user_wallet(user_id)

    text = f"""
💳 **Yᴏᴜʀ Eᴀʀɴɪɴɢ Wᴀʟʟᴇᴛ**

👤 **Uꜱᴇʀ:** {message.from_user.mention}
👀 **Tᴏᴛᴀʟ Vɪᴇᴡꜱ:** `{wallet['views']}`
💰 **Tᴏᴛᴀʟ Bᴀʟᴀɴᴄᴇ:** `৳ {wallet['balance']}`
👥 **Tᴏᴛᴀʟ Rᴇғᴇʀʀᴀʟꜱ:** `{wallet['referrals']}`

*Sʜᴀʀᴇ ʏᴏᴜʀ ғɪʟᴇ ʟɪɴᴋꜱ ᴏʀ ɪɴᴠɪᴛᴇ ғʀɪᴇɴᴅꜱ ᴛᴏ ᴇᴀʀɴ ᴍᴏʀᴇ!*
"""
    # উইথড্র করার জন্য ইনলাইন বাটন সাথে দিয়ে দিলাম
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("💸 Withdraw Money", callback_data="withdraw_money"),
         InlineKeyboardButton("📜 History", callback_data="withdraw_history")]
    ])
    await message.reply_text(text, reply_markup=reply_markup)

# ==========================================
# 🏆 2. LEADERBOARD BUTTON
# ==========================================
@Bot.on_message(filters.regex("^🏆 Leaderboard$") & filters.private)
async def menu_leaderboard(client: Client, message: Message):
    top_users = await get_top_earners(10)
    text = "🏆 **Tᴏᴘ 10 Eᴀʀɴᴇʀꜱ Lᴇᴀᴅᴇʀʙᴏᴀʀᴅ**\n\n"
    medals = ["🥇", "🥈", "🥉", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅"]
    
    if not top_users:
        text += "No earners found yet!"
    else:
        for index, user in enumerate(top_users):
            balance = round(user.get('balance', 0.0), 3)
            views = user.get('views', 0)
            text += f"{medals[index]} **UID:** `{user['_id']}` ➔ ৳ `{balance}` ({views} views)\n"

    await message.reply_text(text)

# ==========================================
# 🔗 3. REFERRAL LINK BUTTON
# ==========================================
@Bot.on_message(filters.regex("^🔗 Referral Link$") & filters.private)
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

# ==========================================
# 👤 4. PROFILE BUTTON
# ==========================================
@Bot.on_message(filters.regex("^👤 My Profile$") & filters.private)
async def menu_profile(client: Client, message: Message):
    user_id = message.from_user.id
    user_data = await get_user(user_id)
    
    if not user_data:
        return await message.reply_text("❌ Profile not found! Please send /start first.")

    join_date = user_data.get("join_date")
    date_str = join_date.strftime("%Y-%m-%d") if join_date else "Unknown"
    warnings = user_data.get("warnings", 0)
    status = "🔴 BANNED" if user_data.get("is_banned") else "🟢 ACTIVE"

    text = f"""
👤 **Uꜱᴇʀ Pʀᴏғɪʟᴇ Sᴛᴀᴛᴜꜱ**

**Nᴀᴍᴇ:** {message.from_user.first_name}
**UID:** `{user_id}`
**Sᴛᴀᴛᴜꜱ:** {status}
**Wᴀʀɴɪɴɢꜱ:** {warnings}/3
**Jᴏɪɴ Dᴀᴛᴇ:** `{date_str}`
**Lᴀɴɢᴜᴀɢᴇ:** `{user_data.get('lang', 'en').upper()}`
"""
    await message.reply_text(text)

# ==========================================
# ⚙️ 5. SETTINGS BUTTON
# ==========================================
@Bot.on_message(filters.regex("^⚙️ Settings$") & filters.private)
async def menu_settings(client: Client, message: Message):
    text = "⚙️ **Yᴏᴜʀ Sᴇᴛᴛɪɴɢꜱ Mᴇɴᴜ**\n\n_Select your preferred language below:_"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"),
         InlineKeyboardButton("🇧🇩 বাংলা", callback_data="set_lang_bn"),
         InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="set_lang_hi")]
    ])
    await message.reply_text(text, reply_markup=reply_markup)

# ==========================================
# ❓ 6. HELP BUTTON
# ==========================================
@Bot.on_message(filters.regex("^❓ Help & Info$") & filters.private)
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
