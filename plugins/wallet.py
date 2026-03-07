# (©) User Wallet & Earning Info System
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from bot import Bot
from database.database import get_user_wallet

# ১. "My Wallet" বাটনে ক্লিক করলে ইউজারের ব্যালেন্স দেখাবে
@Bot.on_callback_query(filters.regex("^my_wallet$"))
async def wallet_callback(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    
    # ডাটাবেস থেকে ইউজারের বর্তমান ভিউ এবং ব্যালেন্স নিয়ে আসবে
    wallet = await get_user_wallet(user_id)
    views = wallet["views"]
    balance = wallet["balance"]

    text = f"""
💳 **Yᴏᴜʀ Eᴀʀɴɪɴɢ Wᴀʟʟᴇᴛ**

👤 **Uꜱᴇʀ:** {query.from_user.mention}
👀 **Tᴏᴛᴀʟ Vɪᴇᴡꜱ:** `{views}`
💰 **Tᴏᴛᴀʟ Bᴀʟᴀɴᴄᴇ:** `৳ {balance}`

*Sʜᴀʀᴇ ʏᴏᴜʀ ғɪʟᴇ ʟɪɴᴋꜱ ᴛᴏ ᴇᴀʀɴ ᴍᴏʀᴇ!*
"""

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("💸 Withdraw Money", callback_data="withdraw_money")],
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ])

    await query.message.edit_text(text, reply_markup=reply_markup)

# ২. "Upload File" বাটনে ক্লিক করলে কাজের নিয়ম দেখাবে
@Bot.on_callback_query(filters.regex("^how_to_upload$"))
async def upload_instructions(client: Client, query: CallbackQuery):
    text = """
📤 **Hᴏᴡ ᴛᴏ Uᴘʟᴏᴀᴅ & Eᴀʀɴ:**

1️⃣ Simply send or forward any file/video to me.
2️⃣ I will instantly generate a unique **Earning Link** for you.
3️⃣ Share that link with your friends or in your channels.
4️⃣ When someone opens the link and receives the file, you earn money! 💸
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Check Wallet", callback_data="my_wallet")],
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ])
    
    await query.message.edit_text(text, reply_markup=reply_markup)

# ৩. "Withdraw Money" বাটনে ক্লিক করলে যা হবে
@Bot.on_callback_query(filters.regex("^withdraw_money$"))
async def withdraw_callback(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    wallet = await get_user_wallet(user_id)
    balance = wallet["balance"]

    # মিনিমাম উইথড্র লিমিট (যেমন: ১০০ টাকা)। আপনি চাইলে এটি পরিবর্তন করতে পারেন।
    MIN_WITHDRAW = 100.0

    if balance < MIN_WITHDRAW:
        await query.answer(f"❌ Minimum withdrawal is ৳{MIN_WITHDRAW}. Your balance is ৳{balance}.", show_alert=True)
        return

    text = f"""
🏦 **Wɪᴛʜᴅʀᴀᴡᴀʟ Rᴇǫᴜᴇꜱᴛ**

Yᴏᴜʀ Bᴀʟᴀɴᴄᴇ: `৳ {balance}`

To withdraw your money, please send a message to the Admin with your payment details (bKash/Nagad/Binance) and your User ID: `{user_id}`
"""
    reply_markup = InlineKeyboardMarkup([
        # URL-এর জায়গায় আপনার নিজের টেলিগ্রাম ইউজারনেম দিন (যেমন: https://t.me/YourUsername)
        [InlineKeyboardButton("👨‍💻 Contact Admin", url="https://t.me/YourUsername")],
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ])
    
    await query.message.edit_text(text, reply_markup=reply_markup)

