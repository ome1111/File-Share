# (©) Premium User Management, F-Sub Control & File Limit System
import time
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message

from bot import Bot
from database.database import get_variable, set_variable, user_data

# ==========================================
# 🛡️ ADMIN CHECKER
# ==========================================
async def is_admin(user_id: int):
    admins = await get_variable("admin", [])
    return user_id in admins

async def check_premium(user_id: int):
    pusers = await get_variable("puser", {})
    if str(user_id) in pusers:
        expiry = pusers[str(user_id)]
        if datetime.now() < expiry:
            return True
        else:
            # Expired, remove from premium
            del pusers[str(user_id)]
            await set_variable("puser", pusers)
            return False
    return False

# ==========================================
# 👑 1. PREMIUM USER MANAGEMENT (Feature 27)
# ==========================================
@Bot.on_message(filters.command("addpremium") & filters.private)
async def add_premium_user(client: Client, message: Message):
    """অ্যাডমিন এই কমান্ড দিয়ে ইউজারকে প্রিমিয়াম বানাতে পারবেন (যাতে তাদের অ্যাড দেখতে না হয়)"""
    if not await is_admin(message.from_user.id): return
    
    if len(message.command) < 3:
        return await message.reply_text("❌ **Usage:** `/addpremium [User ID] [Days]`\nExample: `/addpremium 12345678 30`")
        
    try:
        target_id = int(message.command[1])
        days = int(message.command[2])
        
        pusers = await get_variable("puser", {})
        expiry_date = datetime.now() + timedelta(days=days)
        pusers[str(target_id)] = expiry_date
        
        await set_variable("puser", pusers)
        
        # ইউজারকে মেসেজ পাঠানো
        try:
            await client.send_message(
                chat_id=target_id,
                text=f"🎉 **Cᴏɴɢʀᴀᴛᴜʟᴀᴛɪᴏɴꜱ!**\n\nYou have been upgraded to **Premium User** for `{days}` days! 👑\nNow you can download files directly without watching any ads."
            )
        except:
            pass
            
        await message.reply_text(f"✅ **Success!** User `{target_id}` is now Premium until {expiry_date.strftime('%Y-%m-%d')}.")
    except ValueError:
        await message.reply_text("❌ **Invalid Format! User ID and Days must be numbers.**")

@Bot.on_message(filters.command("delpremium") & filters.private)
async def del_premium_user(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/delpremium [User ID]`")
        
    try:
        target_id = str(message.command[1])
        pusers = await get_variable("puser", {})
        
        if target_id in pusers:
            del pusers[target_id]
            await set_variable("puser", pusers)
            await message.reply_text(f"✅ **Success!** User `{target_id}` removed from Premium list.")
        else:
            await message.reply_text("❌ **User is not Premium!**")
    except Exception as e:
        await message.reply_text(f"❌ **Error:** `{e}`")

# ==========================================
# 📢 2. DYNAMIC F-SUB CONTROL (Feature 23)
# ==========================================
@Bot.on_message(filters.command(["addfsub", "delfsub"]) & filters.private)
async def manage_fsub(client: Client, message: Message):
    """ওয়েব প্যানেল ছাড়াই টেলিগ্রাম থেকে Force Subscribe চ্যানেল অ্যাড বা রিমুভ করা"""
    if not await is_admin(message.from_user.id): return
    
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/addfsub [Channel ID/Username]` or `/delfsub [Channel ID]`")
        
    channel_id = message.command[1]
    fsub_list = await get_variable("fsub_channels", [])
    
    if message.command[0] == "addfsub":
        if channel_id not in fsub_list:
            fsub_list.append(channel_id)
            await set_variable("fsub_channels", fsub_list)
            await message.reply_text(f"✅ **Channel added to F-Sub list:** `{channel_id}`")
        else:
            await message.reply_text("⚠️ **Channel is already in the list!**")
            
    elif message.command[0] == "delfsub":
        if channel_id in fsub_list:
            fsub_list.remove(channel_id)
            await set_variable("fsub_channels", fsub_list)
            await message.reply_text(f"🗑️ **Channel removed from F-Sub list:** `{channel_id}`")
        else:
            await message.reply_text("❌ **Channel not found in the list!**")

@Bot.on_message(filters.command("fsubs") & filters.private)
async def list_fsubs(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    
    fsub_list = await get_variable("fsub_channels", [])
    if not fsub_list:
        return await message.reply_text("📜 **No channels are currently set for Force Subscribe.**")
        
    text = "📢 **Cᴜʀʀᴇɴᴛ F-Sᴜʙ Cʜᴀɴɴᴇʟꜱ:**\n\n"
    for idx, ch in enumerate(fsub_list, 1):
        text += f"{idx}. `{ch}`\n"
        
    await message.reply_text(text)

# ==========================================
# 📁 3. FILE SIZE LIMIT SYSTEM (Feature 19)
# ==========================================
# Group -1 means this handler will run BEFORE any other download/upload handlers
@Bot.on_message(filters.private & (filters.document | filters.video | filters.audio), group=-1)
async def check_file_size(client: Client, message: Message):
    """সাধারণ ইউজারদের জন্য ম্যাক্সিমাম সাইজ লিমিট (যেমন: ২ জিবি) চেক করবে"""
    file_size = 0
    if message.document: file_size = message.document.file_size
    elif message.video: file_size = message.video.file_size
    elif message.audio: file_size = message.audio.file_size
    
    # ২ জিবি লিমিট (বাইটে হিসাব করা)
    MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024 
    
    if file_size > MAX_FILE_SIZE:
        is_prem = await check_premium(message.from_user.id)
        if not is_prem:
            await message.reply_text(
                "⚠️ **Fɪʟᴇ Sɪᴢᴇ Lɪᴍɪᴛ Exᴄᴇᴇᴅᴇᴅ!**\n\n"
                "Normal users can only upload files up to **2 GB**. To upload larger files, please upgrade to **Premium**! 👑",
                quote=True
            )
            message.stop_propagation() # ফাইলটি এখানেই ব্লক করে দেবে, অন্য কোনো ফাইলে যাবে না
