# (©) Persistent Bottom Menu System (Upgraded for Async DB)
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot import Bot
from database.database import user_data, get_variable

# ==========================================
# 📤 0. UPLOAD FILE BUTTON
# ==========================================
@Bot.on_message(filters.regex(r"Upload File") & filters.private)
async def menu_upload(client: Client, message: Message):
    text = (
        "📤 **How to Upload & Earn:**\n\n"
        "It's very simple! Just send me any **File, Video, Photo, Audio, or a Web URL** directly here in this chat.\n\n"
        "I will instantly convert it into a monetized shortlink. Share that link with your friends and start earning! 💸"
    )
    await message.reply_text(text)

# ==========================================
# 🎛️ 1. WALLET BUTTON
# ==========================================
@Bot.on_message(filters.regex(r"My Wallet") & filters.private)
async def menu_wallet(client: Client, message: Message):
    user_id = message.from_user.id
    
    # ডাটাবেস থেকে ইউজারের ডাটা আনা
    user = await user_data.find_one({"_id": user_id})
    views = user.get("views", 0) if user else 0
    balance = round(user.get("balance", 0.0), 3) if user else 0.0
    referrals = user.get("referrals", 0) if user else 0

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

# ==========================================
# 🏆 2. LEADERBOARD BUTTON
# ==========================================
@Bot.on_message(filters.regex(r"Leaderboard") & filters.private)
async def menu_leaderboard(client: Client, message: Message):
    wait_msg = await message.reply_text("🔄 **Fetching Top Earners...**", quote=True)
    
    top_users = await user_data.find().sort("balance", -1).limit(10).to_list(10)
    text = "🏆 **Tᴏᴘ 10 Eᴀʀɴᴇʀꜱ Lᴇᴀᴅᴇʀʙᴏᴀʀᴅ**\n\n"
    medals = ["🥇", "🥈", "🥉", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅", "🏅"]
    
    if not top_users:
        text += "No earners found yet!"
    else:
        for index, user in enumerate(top_users):
            balance = round(user.get('balance', 0.0), 3)
            views = user.get('views', 0)
            uid = user.get('_id')
            hidden_uid = f"{str(uid)[:4]}***{str(uid)[-2:]}"
            text += f"{medals[index]} **UID:** `{hidden_uid}` ➔ ৳ `{balance}` ({views} views)\n"

    await wait_msg.edit_text(text)

# ==========================================
# 🔗 3. REFERRAL LINK BUTTON
# ==========================================
@Bot.on_message(filters.regex(r"Referral Link") & filters.private)
async def menu_referral(client: Client, message: Message):
    user_id = message.from_user.id
    bot_username = client.me.username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    text = f"""
🔗 **Yᴏᴜʀ Rᴇғᴇʀʀᴀʟ Lɪɴᴋ**

`{ref_link}`

🎁 **Bᴏɴᴜs:**
Invite your friends using this link. When they join and earn money, you will get a **lifetime commission** from their earnings automatically!
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={ref_link}")]
    ])
    await message.reply_text(text, reply_markup=reply_markup, disable_web_page_preview=True)

# ==========================================
# 👤 4. PROFILE BUTTON
# ==========================================
@Bot.on_message(filters.regex(r"My Profile") & filters.private)
async def menu_profile(client: Client, message: Message):
    user_id = message.from_user.id
    user = await user_data.find_one({"_id": user_id})
    
    if not user:
        return await message.reply_text("❌ Profile not found! Please send /start first.")

    join_date = user.get("join_date")
    date_str = join_date.strftime("%Y-%m-%d") if join_date else "Unknown"
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

# ==========================================
# ⚙️ 5. SETTINGS BUTTON
# ==========================================
@Bot.on_message(filters.regex(r"Settings") & filters.private)
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
@Bot.on_message(filters.regex(r"Help & Info") & filters.private)
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
