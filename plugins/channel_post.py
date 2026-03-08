# (©)@Nation_Bots (Upgraded for Custom Ad Network & Earning System)

import asyncio

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot import Bot
from config import CHANNEL_ID
from database.database import get_variable
from helper_func import encode, get_shortlink

DISABLE_CHANNEL_BUTTON = False


@Bot.on_message(
    filters.private
    & (filters.document | filters.video | filters.audio | filters.photo) 
    & ~filters.command(
        [
            "start",
            "users",
            "broadcast",
            "total",
            "clear",
            "batch",
            "genlink",
            "stats",
            "senduser",
            "file",
            "fsub",
            "shortner",
            "admin",
            "auto_del",
            "restart",
        ]
    )
)
async def channel_post(client: Client, message: Message):
    """অ্যাডমিনরা বটের ইনবক্সে কোনো ফাইল দিলে তার আর্নিং লিংক তৈরি করবে"""
    admin = await get_variable("admin", [])
    userid = message.from_user.id
    if userid not in admin:
        return
        
    reply_text = await message.reply_text("⏳ Processing your link...", quote=True)
    try:
        post_message = await message.copy(
            chat_id=client.db_channel.id, disable_notification=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.value if hasattr(e, 'value') else e.x)
        post_message = await message.copy(
            chat_id=client.db_channel.id, disable_notification=True
        )
    except Exception as e:
        print(f"Error copying admin file: {e}")
        await reply_text.edit_text("❌ Something went wrong while processing your file.")
        return

    converted_id = post_message.id * abs(client.db_channel.id)
    # চ্যানেলের পোস্টের জন্য সাধারণ get- ট্যাগ ব্যবহার করা হলো
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    
    bot_username = client.me.username
    bot_link = f"https://t.me/{bot_username}?start={base64_string}"
    
    # 🔥 FIX: user_id পাঠানো হলো, যাতে ফাইল আপলোডার (অ্যাডমিন) টাকা পায়!
    short_link = await get_shortlink(bot_link, user_id=userid)

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔁 Share Earning Link", url=f"https://telegram.me/share/url?url={short_link}"
                )
            ]
        ]
    )

    await reply_text.edit(
        f"✅ **Here is your Monetized Link:**\n\n`{short_link}`",
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )

    if not DISABLE_CHANNEL_BUTTON:
        await post_message.edit_reply_markup(reply_markup)


@Bot.on_message(filters.channel & filters.incoming & filters.chat(CHANNEL_ID))
async def new_post(client: Client, message: Message):
    """অ্যাডমিন সরাসরি ডাটাবেস চ্যানেলে কিছু আপলোড দিলে তার নিচে বাটন অ্যাড করবে"""
    if DISABLE_CHANNEL_BUTTON:
        return

    converted_id = message.id * abs(client.db_channel.id)
    string = f"get-{converted_id}"
    base64_string = await encode(string)
    
    bot_username = client.me.username
    bot_link = f"https://t.me/{bot_username}?start={base64_string}"
    
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔁 Share URL", url=f"https://telegram.me/share/url?url={bot_link}"
                )
            ]
        ]
    )
    
    try:
        await message.edit_reply_markup(reply_markup)
    except Exception:
        pass
