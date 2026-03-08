# (©) Premium User Management, F-Sub Control & File Limit System
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
from bot import Bot
from database.database import get_variable, set_variable

async def is_admin(user_id: int):
    admins = await get_variable("admin", [])
    return user_id in admins

async def check_premium(user_id: int):
    pusers = await get_variable("puser", {})
    if str(user_id) in pusers:
        if datetime.now() < pusers[str(user_id)]: return True
        else:
            del pusers[str(user_id)]
            await set_variable("puser", pusers)
    return False

# ==========================================
# 👑 1. PREMIUM USER MANAGEMENT
# ==========================================
@Bot.on_message(filters.command("addpremium") & filters.private)
async def add_premium_user(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    try:
        target_id, days = int(message.command[1]), int(message.command[2])
        pusers = await get_variable("puser", {})
        expiry_date = datetime.now() + timedelta(days=days)
        pusers[str(target_id)] = expiry_date
        await set_variable("puser", pusers)
        try: await client.send_message(target_id, f"🎉 **Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ!**\n\nYou are now a **Premium User** for `{days}` days! 👑")
        except: pass
        await message.reply_text(f"✅ User `{target_id}` is Premium until {expiry_date.strftime('%Y-%m-%d')}.")
    except: await message.reply_text("❌ **Usage:** `/addpremium [User ID] [Days]`")

@Bot.on_message(filters.command("delpremium") & filters.private)
async def del_premium_user(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    try:
        target_id = str(message.command[1])
        pusers = await get_variable("puser", {})
        if target_id in pusers:
            del pusers[target_id]
            await set_variable("puser", pusers)
            await message.reply_text(f"✅ User `{target_id}` removed from Premium.")
        else: await message.reply_text("❌ User is not Premium!")
    except: await message.reply_text("❌ **Usage:** `/delpremium [User ID]`")

# ==========================================
# 📢 2. DYNAMIC F-SUB CONTROL
# ==========================================
@Bot.on_message(filters.command(["addfsub", "delfsub"]) & filters.private)
async def manage_fsub(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    if len(message.command) < 2: return await message.reply_text("❌ **Usage:** `/addfsub [Channel ID]` or `/delfsub [Channel ID]`")
        
    channel_id = message.command[1]
    raw_fsub = await get_variable("F_sub", "")
    fsub_list = [x.strip() for x in raw_fsub.split() if x.strip()]
    
    if message.command[0] == "addfsub":
        if channel_id not in fsub_list:
            fsub_list.append(channel_id)
            await set_variable("F_sub", " ".join(fsub_list))
            await message.reply_text(f"✅ **Channel added to F-Sub list:** `{channel_id}`")
        else: await message.reply_text("⚠️ **Channel is already in the list!**")
            
    elif message.command[0] == "delfsub":
        if channel_id in fsub_list:
            fsub_list.remove(channel_id)
            await set_variable("F_sub", " ".join(fsub_list))
            await message.reply_text(f"🗑️ **Channel removed from F-Sub list:** `{channel_id}`")
        else: await message.reply_text("❌ **Channel not found!**")

@Bot.on_message(filters.command("fsubs") & filters.private)
async def list_fsubs(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    raw_fsub = await get_variable("F_sub", "")
    fsub_list = [x.strip() for x in raw_fsub.split() if x.strip()]
    if not fsub_list: return await message.reply_text("📜 **No F-Sub channels set.**")
    text = "📢 **Cᴜʀʀᴇɴᴛ F-Sᴜʙ Cʜᴀɴɴᴇʟꜱ:**\n\n" + "\n".join([f"{i}. `{c}`" for i, c in enumerate(fsub_list, 1)])
    await message.reply_text(text)

# ==========================================
# 📁 3. FILE SIZE LIMIT SYSTEM
# ==========================================
@Bot.on_message(filters.private & (filters.document | filters.video | filters.audio), group=-1)
async def check_file_size(client: Client, message: Message):
    file_size = getattr(message.document or message.video or message.audio, 'file_size', 0)
    if file_size > (2 * 1024 * 1024 * 1024): # 2GB Limit
        if not await check_premium(message.from_user.id):
            await message.reply_text("⚠️ **Fɪʟᴇ Sɪᴢᴇ Lɪᴍɪᴛ Exᴄᴇᴇᴅᴇᴅ!**\nNormal users can only upload up to **2 GB**. Upgrade to Premium!", quote=True)
            message.stop_propagation()
