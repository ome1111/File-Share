# (©) Advanced User Wallet, Profile & Referral System
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message

from bot import Bot
from database.database import (
    get_user_wallet, get_user, get_top_earners, 
    get_withdrawal_history, add_withdrawal_request
)

# ==========================================
# 💰 1. MY WALLET MENU
# ==========================================
@Bot.on_callback_query(filters.regex("^my_wallet$"))
async def wallet_callback(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    wallet = await get_user_wallet(user_id)

    text = f"""
💳 **Yᴏᴜʀ Eᴀʀɴɪɴɢ Wᴀʟʟᴇᴛ**

👤 **Uꜱᴇʀ:** {query.from_user.mention}
👀 **Tᴏᴛᴀʟ Vɪᴇᴡꜱ:** `{wallet['views']}`
💰 **Tᴏᴛᴀʟ Bᴀʟᴀɴᴄᴇ:** `৳ {wallet['balance']}`
👥 **Tᴏᴛᴀʟ Rᴇғᴇʀʀᴀʟꜱ:** `{wallet['referrals']}`

*Sʜᴀʀᴇ ʏᴏᴜʀ ғɪʟᴇ ʟɪɴᴋꜱ ᴏʀ ɪɴᴠɪᴛᴇ ғʀɪᴇɴᴅꜱ ᴛᴏ ᴇᴀʀɴ ᴍᴏʀᴇ!*
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("💸 Withdraw Money", callback_data="withdraw_money"),
         InlineKeyboardButton("📜 History", callback_data="withdraw_history")],
        [InlineKeyboardButton("🔗 My Referral Link", callback_data="my_referral")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leaderboard"),
         InlineKeyboardButton("👤 Profile", callback_data="my_profile")],
        [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="back_to_start")]
    ])
    await query.message.edit_text(text, reply_markup=reply_markup)

# ==========================================
# 📤 2. HOW TO UPLOAD
# ==========================================
@Bot.on_callback_query(filters.regex("^how_to_upload$"))
async def upload_instructions(client: Client, query: CallbackQuery):
    text = """
📤 **Hᴏᴡ ᴛᴏ Uᴘʟᴏᴀᴅ & Eᴀʀɴ:**

1️⃣ Send or forward any file/video to me.
2️⃣ I will generate a unique **Earning Link**.
3️⃣ Share it with friends or channels.
4️⃣ When someone opens the link, you get views & money! 💸
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Check Wallet", callback_data="my_wallet")],
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ])
    await query.message.edit_text(text, reply_markup=reply_markup)

# ==========================================
# 👥 3. REFERRAL SYSTEM (Feature 1)
# ==========================================
@Bot.on_callback_query(filters.regex("^my_referral$"))
async def referral_callback(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    bot_username = client.me.username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    text = f"""
🔗 **Yᴏᴜʀ Rᴇғᴇʀʀᴀʟ Lɪɴᴋ**

`{ref_link}`

🎁 **Bᴏɴᴜs:**
Invite your friends using this link. When they join and earn money, you will get a **5% lifetime commission** from their earnings automatically!
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={ref_link}")],
        [InlineKeyboardButton("🔙 Back", callback_data="my_wallet")]
    ])
    await query.message.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=True)

# ==========================================
# 🏆 4. LEADERBOARD (Feature 6)
# ==========================================
@Bot.on_callback_query(filters.regex("^leaderboard$"))
async def leaderboard_callback(client: Client, query: CallbackQuery):
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

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="my_wallet")]])
    await query.message.edit_text(text, reply_markup=reply_markup)

# ==========================================
# 👤 5. MY PROFILE (Feature 34)
# ==========================================
@Bot.on_callback_query(filters.regex("^my_profile$"))
async def profile_callback(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    user_data = await get_user(user_id)
    
    if not user_data:
        return await query.answer("Profile not found!", show_alert=True)

    join_date = user_data.get("join_date")
    date_str = join_date.strftime("%Y-%m-%d") if join_date else "Unknown"
    warnings = user_data.get("warnings", 0)
    status = "🔴 BANNED" if user_data.get("is_banned") else "🟢 ACTIVE"

    text = f"""
👤 **Uꜱᴇʀ Pʀᴏғɪʟᴇ Sᴛᴀᴛᴜꜱ**

**Nᴀᴍᴇ:** {query.from_user.first_name}
**UID:** `{user_id}`
**Sᴛᴀᴛᴜꜱ:** {status}
**Wᴀʀɴɪɴɢꜱ:** {warnings}/3
**Jᴏɪɴ Dᴀᴛᴇ:** `{date_str}`
**Lᴀɴɢᴜᴀɢᴇ:** `{user_data.get('lang', 'en').upper()}`
"""
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="my_wallet")]])
    await query.message.edit_text(text, reply_markup=reply_markup)

# ==========================================
# 📜 6. WITHDRAWAL HISTORY (Feature 3)
# ==========================================
@Bot.on_callback_query(filters.regex("^withdraw_history$"))
async def history_callback(client: Client, query: CallbackQuery):
    history = await get_withdrawal_history(query.from_user.id)
    text = "📜 **Yᴏᴜʀ Rᴇᴄᴇɴᴛ Wɪᴛʜᴅʀᴀᴡᴀʟꜱ**\n\n"
    
    if not history:
        text += "You have no withdrawal history yet."
    else:
        for req in history:
            date_str = req["date"].strftime("%d %b, %y")
            status_icon = "⏳" if req["status"] == "Pending" else "✅" if req["status"] == "Paid" else "❌"
            text += f"**[{date_str}]** ৳ {req['amount']} - {req['method']}\nStatus: {status_icon} {req['status']}\n\n"

    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="my_wallet")]])
    await query.message.edit_text(text, reply_markup=reply_markup)

# ==========================================
# 💸 7. WITHDRAW REQUEST SYSTEM (Feature 21)
# ==========================================
@Bot.on_callback_query(filters.regex("^withdraw_money$"))
async def withdraw_callback(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    wallet = await get_user_wallet(user_id)
    balance = wallet["balance"]
    MIN_WITHDRAW = 100.0

    if balance < MIN_WITHDRAW:
        return await query.answer(f"❌ Minimum withdrawal is ৳{MIN_WITHDRAW}. Your balance is ৳{balance}.", show_alert=True)

    text = f"""
🏦 **Wɪᴛʜᴅʀᴀᴡᴀʟ Rᴇǫᴜᴇꜱᴛ**

Yᴏᴜʀ Bᴀʟᴀɴᴄᴇ: `৳ {balance}`

To request a withdrawal, send a message using this format:
`/withdraw [Amount] [Method] [Details]`

**Example:**
`/withdraw {balance} bKash 017XXXXXXX`
"""
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="my_wallet")]])
    await query.message.edit_text(text, reply_markup=reply_markup)

# Handle the /withdraw command
@Bot.on_message(filters.command("withdraw") & filters.private)
async def process_withdraw_command(client: Client, message: Message):
    user_id = message.from_user.id
    args = message.text.split(" ", 3)
    
    if len(args) < 4:
        return await message.reply("❌ **Invalid Format!**\nUse: `/withdraw [Amount] [Method] [Account Details]`\nExample: `/withdraw 150 Nagad 019XXXXXXX`")
    
    try:
        amount = float(args[1])
        method = args[2]
        details = args[3]
    except ValueError:
        return await message.reply("❌ Invalid amount format.")

    wallet = await get_user_wallet(user_id)
    if amount < 100.0:
        return await message.reply("❌ Minimum withdrawal is ৳100.")
    if amount > wallet["balance"]:
        return await message.reply(f"❌ Insufficient balance! Your balance is ৳{wallet['balance']}.")

    # ডাটাবেসে উইথড্র রিকোয়েস্ট সেভ করা
    success = await add_withdrawal_request(user_id, amount, method, details)
    if success:
        await message.reply(f"✅ **Withdrawal Request Successful!**\nAmount: ৳{amount}\nMethod: {method}\n\n_Your request is pending and will be checked by the Admin._")
    else:
        await message.reply("❌ Something went wrong. Please try again later.")
