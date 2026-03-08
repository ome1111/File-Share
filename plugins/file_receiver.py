# (©) Unified File Receiver & Earning System
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from bot import Bot
from database.database import get_variable
from helper_func import encode, get_shortlink

@Bot.on_message(
    filters.private 
    & (filters.document | filters.video | filters.audio | filters.photo)
    & ~filters.command(["start", "users", "broadcast", "addfsub", "delfsub", "withdraw", "stats", "senduser", "rename"])
)
async def handle_all_uploads(client: Client, message: Message):
    user_id = message.from_user.id
    admin_list = await get_variable("admin", [])
    
    reply_text = await message.reply_text("⏳ *Processing your file for monetized link...*", quote=True)
    
    try:
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.value + 1)
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except Exception as e:
        await reply_text.edit_text("❌ Something went wrong while saving your file.")
        return

    converted_id = post_message.id * abs(client.db_channel.id)
    
    # 🎯 লজিক: অ্যাডমিন হলে নরমাল লিংক (get-), আর ইউজার হলে আর্নিং লিংক (earn-) পাবে!
    if user_id in admin_list:
        string = f"get-{converted_id}"
    else:
        string = f"earn-{converted_id}-{user_id}"
        
    base64_string = await encode(string)
    bot_link = f"https://t.me/{client.me.username}?start={base64_string}"
    
    # শর্টলিংক জেনারেট করা
    short_link = await get_shortlink(bot_link, user_id=user_id)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share Earning Link", url=f"https://telegram.me/share/url?url={short_link}")]])

    # মেসেজ ডেলিভারি
    if user_id in admin_list:
        msg_text = f"✅ **Admin Link Generated!**\n\n🔗 `{short_link}`"
        await post_message.edit_reply_markup(reply_markup) # ডাটাবেস চ্যানেলেও বাটন বসাবে
    else:
        msg_text = f"🎉 **File Uploaded Successfully!**\n\n🔗 **Your Earning Link:**\n`{short_link}`\n\n💸 *Share this link to earn money!*"
        
    await reply_text.edit(msg_text, reply_markup=reply_markup, disable_web_page_preview=True)

@Bot.on_message(filters.channel & filters.incoming)
async def new_channel_post(client: Client, message: Message):
    """অ্যাডমিন সরাসরি ডাটাবেস চ্যানেলে কিছু আপলোড দিলে তার নিচে বাটন অ্যাড করবে"""
    if message.chat.id != client.db_channel.id: return
    try:
        converted_id = message.id * abs(client.db_channel.id)
        base64_string = await encode(f"get-{converted_id}")
        bot_link = f"https://t.me/{client.me.username}?start={base64_string}"
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={bot_link}")]])
        await message.edit_reply_markup(reply_markup)
    except: pass
