# (©) Unified File, Album & Batch Receiver System with Smart Button
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from bot import Bot
from database.database import get_variable
from helper_func import encode, get_shortlink

media_groups = {}
batch_users = {}  # ব্যাচ মোডে থাকা ইউজারদের ট্র্যাক করার জন্য

# ==========================================
# 📦 0. SMART UPLOAD BUTTON & BATCH MODE
# ==========================================
@Bot.on_message(filters.private & (filters.command("batch") | filters.regex("^📤 Upload File$")))
async def start_batch(client: Client, message: Message):
    batch_users[message.from_user.id] = []
    text = (
        "📤 **Upload Mode Activated!**\n\n"
        "Please send or forward all the files, videos, or photos you want to share.\n"
        "I will safely collect them in the background.\n\n"
        "👇 **When you are completely finished sending files, click the button below:**"
    )
    markup = InlineKeyboardMarkup([[InlineKeyboardButton("✅ Upload Done", callback_data="upload_done")]])
    await message.reply_text(text, reply_markup=markup)

@Bot.on_message(filters.private & filters.command("done"))
async def finish_batch_cmd(client: Client, message: Message):
    await process_batch_files(client, message.from_user.id, message)

@Bot.on_callback_query(filters.regex("^upload_done$"))
async def finish_batch_callback(client: Client, callback_query: CallbackQuery):
    await process_batch_files(client, callback_query.from_user.id, callback_query.message, is_callback=True)

async def process_batch_files(client, user_id, message, is_callback=False):
    if user_id not in batch_users:
        text = "❌ You are not in Upload Mode! Click '📤 Upload File' first."
        if is_callback:
            return await message.answer(text, show_alert=True)
        else:
            return await message.reply_text(text)
        
    messages = batch_users[user_id]
    if not messages:
        del batch_users[user_id]
        text = "❌ You didn't send any files! Upload session cancelled."
        if is_callback:
            await message.delete()
            return await message.reply_text(text)
        else:
            return await message.reply_text(text)

    # লোডিং মেসেজ দেখানো
    if is_callback:
        wait_msg = message
        await wait_msg.edit_text(f"⏳ *Processing {len(messages)} files for a single link...*")
    else:
        wait_msg = await message.reply_text(f"⏳ *Processing {len(messages)} files for a single link...*", quote=True)
        
    admin_list = await get_variable("admin", [])
    messages.sort(key=lambda x: x.id) # ফাইল সিরিয়াল করা
    
    copied_msgs = []
    for msg in messages:
        try:
            copied = await msg.copy(chat_id=client.db_channel.id, disable_notification=True)
            copied_msgs.append(copied)
            await asyncio.sleep(0.5)
        except Exception:
            pass
            
    del batch_users[user_id]

    if not copied_msgs:
        return await wait_msg.edit_text("❌ Failed to process files.")

    first_id = copied_msgs[0].id * abs(client.db_channel.id)
    last_id = copied_msgs[-1].id * abs(client.db_channel.id)

    # লিংক জেনারেট
    if user_id in admin_list:
        string = f"get-{first_id}-{last_id}"
    else:
        string = f"earn-{first_id}-{last_id}-{user_id}"
        
    base64_string = await encode(string)
    bot_link = f"https://t.me/{client.me.username}?start={base64_string}"
    short_link = await get_shortlink(bot_link, user_id=user_id)
    
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={short_link}")]])
    
    if user_id in admin_list:
        text = f"✅ **Admin Batch Link Generated!**\n\n📁 **Total Files:** `{len(copied_msgs)}`\n🔗 `{short_link}`"
    else:
        text = f"🎉 **Upload Completed!**\n\n📁 **Total Files:** `{len(copied_msgs)}`\n🔗 **Your Earning Link:**\n`{short_link}`\n\n💸 *Share this link to earn money!*"
        
    await wait_msg.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=True)


# ==========================================
# 📂 1. ALBUM BATCH HANDLER
# ==========================================
@Bot.on_message(
    filters.private 
    & filters.media_group
    & (filters.document | filters.video | filters.audio | filters.photo)
)
async def handle_albums(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in batch_users:
        batch_users[user_id].append(message)
        return

    group_id = message.media_group_id
    admin_list = await get_variable("admin", [])

    if group_id not in media_groups:
        media_groups[group_id] = [message]
        wait_msg = await message.reply_text("⏳ *Processing your album for a single monetized link...*", quote=True)
        await asyncio.sleep(3) 
        messages = media_groups.pop(group_id)
        messages.sort(key=lambda x: x.id) 
        copied_msgs = []
        for msg in messages:
            try:
                copied = await msg.copy(chat_id=client.db_channel.id, disable_notification=True)
                copied_msgs.append(copied)
                await asyncio.sleep(0.5)
            except Exception:
                pass
        if not copied_msgs:
            return await wait_msg.edit_text("❌ Failed to process album.")

        first_id = copied_msgs[0].id * abs(client.db_channel.id)
        last_id = copied_msgs[-1].id * abs(client.db_channel.id)

        if user_id in admin_list:
            string = f"get-{first_id}-{last_id}"
        else:
            string = f"earn-{first_id}-{last_id}-{user_id}"
            
        base64_string = await encode(string)
        bot_link = f"https://t.me/{client.me.username}?start={base64_string}"
        short_link = await get_shortlink(bot_link, user_id=user_id)
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share Album Link", url=f"https://telegram.me/share/url?url={short_link}")]])
        
        if user_id in admin_list:
            text = f"✅ **Admin Batch Link Generated!**\n\n📁 **Total Files:** `{len(copied_msgs)}`\n🔗 `{short_link}`"
        else:
            text = f"🎉 **Album Uploaded Successfully!**\n\n📁 **Total Files:** `{len(copied_msgs)}`\n🔗 **Your Earning Link:**\n`{short_link}`\n\n💸 *Share this link to earn money!*"
            
        await wait_msg.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=True)
    else:
        media_groups[group_id].append(message)


# ==========================================
# 📄 2. SINGLE FILE HANDLER
# ==========================================
@Bot.on_message(
    filters.private 
    & ~filters.media_group 
    & (filters.document | filters.video | filters.audio | filters.photo)
    & ~filters.command(["start", "users", "broadcast", "addfsub", "delfsub", "withdraw", "stats", "senduser", "rename", "batch", "done"])
)
async def handle_single_upload(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in batch_users:
        batch_users[user_id].append(message)
        return

    admin_list = await get_variable("admin", [])
    reply_text = await message.reply_text("⏳ *Processing your file for monetized link...*", quote=True)
    
    try:
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except FloodWait as e:
        await asyncio.sleep(e.value + 1)
        post_message = await message.copy(chat_id=client.db_channel.id, disable_notification=True)
    except Exception:
        return await reply_text.edit_text("❌ Something went wrong while saving your file.")

    converted_id = post_message.id * abs(client.db_channel.id)
    
    if user_id in admin_list:
        string = f"get-{converted_id}"
    else:
        string = f"earn-{converted_id}-{user_id}"
        
    base64_string = await encode(string)
    bot_link = f"https://t.me/{client.me.username}?start={base64_string}"
    short_link = await get_shortlink(bot_link, user_id=user_id)
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share Earning Link", url=f"https://telegram.me/share/url?url={short_link}")]])

    if user_id in admin_list:
        msg_text = f"✅ **Admin Link Generated!**\n\n🔗 `{short_link}`"
        await post_message.edit_reply_markup(reply_markup)
    else:
        msg_text = f"🎉 **File Uploaded Successfully!**\n\n🔗 **Your Earning Link:**\n`{short_link}`\n\n💸 *Share this link to earn money!*"
        
    await reply_text.edit(msg_text, reply_markup=reply_markup, disable_web_page_preview=True)

# ==========================================
# 📺 3. CHANNEL AUTO-BUTTON SYSTEM
# ==========================================
@Bot.on_message(filters.channel & filters.incoming)
async def new_channel_post(client: Client, message: Message):
    if message.chat.id != client.db_channel.id: return
    try:
        converted_id = message.id * abs(client.db_channel.id)
        base64_string = await encode(f"get-{converted_id}")
        bot_link = f"https://t.me/{client.me.username}?start={base64_string}"
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔁 Share URL", url=f"https://telegram.me/share/url?url={bot_link}")]])
        await message.edit_reply_markup(reply_markup)
    except: pass
