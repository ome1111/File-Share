# (©) Advanced Admin Tools: Scheduler, DB Backup, Premium Reminder & Log System
import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

from bot import Bot
from database.database import get_variable, set_variable, full_userbase

# ==========================================
# 🛡️ ADMIN CHECKER
# ==========================================
async def is_admin(user_id: int):
    admins = await get_variable("admin", [])
    return user_id in admins

# ==========================================
# 🕒 1. BROADCAST SCHEDULING (Feature 38)
# ==========================================
@Bot.on_message(filters.command("sbroadcast") & filters.private)
async def scheduled_broadcast(client: Client, message: Message):
    """একটি নির্দিষ্ট সময় পর অটোমেটিক ব্রডকাস্ট করার সিস্টেম"""
    if not await is_admin(message.from_user.id): return
    
    if not message.reply_to_message:
        return await message.reply_text("❌ **Please reply to a message/file you want to schedule!**")
        
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/sbroadcast [Delay in Minutes]`\nExample: `/sbroadcast 60` (Broadcasts after 1 hour)")
        
    try:
        delay_minutes = int(message.command[1])
        await message.reply_text(f"✅ **Broadcast Scheduled!**\nIt will automatically start after `{delay_minutes}` minutes. You can close Telegram now.")
        
        # ব্যাকগ্রাউন্ড টাস্ক (যা নির্দিষ্ট সময় পর কাজ শুরু করবে)
        async def do_broadcast():
            await asyncio.sleep(delay_minutes * 60)
            users = await full_userbase()
            success, failed = 0, 0
            
            for uid in users:
                try:
                    await message.reply_to_message.copy(uid)
                    success += 1
                    await asyncio.sleep(0.5) # FloodWait এড়ানোর জন্য
                except:
                    failed += 1
                    
            # ব্রডকাস্ট শেষ হলে অ্যাডমিনকে রিপোর্ট দেওয়া
            try:
                await client.send_message(
                    chat_id=message.from_user.id,
                    text=f"📢 **Scheduled Broadcast Completed!**\n\n✅ Success: `{success}`\n❌ Failed: `{failed}`"
                )
            except: pass
            
        # টাস্কটি রান করে দেওয়া হলো
        asyncio.create_task(do_broadcast())
        
    except ValueError:
        await message.reply_text("❌ **Delay must be a valid number!**")

# ==========================================
# 🔄 2. DATABASE BACKUP SYSTEM (Feature 13)
# ==========================================
@Bot.on_message(filters.command("backup_db") & filters.private)
async def backup_database_channel(client: Client, message: Message):
    """এক চ্যানেল থেকে আরেক চ্যানেলে সব ফাইল কপি করার ম্যাজিক কমান্ড"""
    if not await is_admin(message.from_user.id): return
    
    if len(message.command) < 3:
        return await message.reply_text("❌ **Usage:** `/backup_db [Source_Channel_ID] [Destination_Channel_ID]`\n\n_Note: The bot must be an admin in both channels._")
        
    try:
        source_chat = int(message.command[1])
        dest_chat = int(message.command[2])
        
        wait_msg = await message.reply_text("⏳ **Starting Database Backup...** This might take a long time depending on your files.")
        
        copied_count = 0
        # সোর্স চ্যানেল থেকে সব মেসেজ স্ক্যান করা
        async for msg in client.get_chat_history(source_chat):
            if msg.document or msg.video or msg.audio or msg.photo:
                try:
                    await msg.copy(dest_chat)
                    copied_count += 1
                    await asyncio.sleep(2) # টেলিগ্রামের লিমিট থেকে বাঁচতে
                except FloodWait as e:
                    await asyncio.sleep(e.value + 2)
                    await msg.copy(dest_chat)
                    copied_count += 1
                except Exception:
                    pass
                    
        await wait_msg.edit_text(f"✅ **Backup Complete!**\nSuccessfully copied `{copied_count}` files to the new channel.")
        
    except ValueError:
        await message.reply_text("❌ **Channel IDs must be numbers (e.g., -100123456789).**")
    except Exception as e:
        await message.reply_text(f"❌ **Error:** `{e}`")

# ==========================================
# 👑 3. PREMIUM AUTO-REMINDER (Feature 30)
# ==========================================
@Bot.on_message(filters.command("remind_premium") & filters.private)
async def send_premium_reminders(client: Client, message: Message):
    """যাদের প্রিমিয়াম ৩ দিনের মধ্যে শেষ হবে, তাদের রিমাইন্ডার পাঠানো"""
    if not await is_admin(message.from_user.id): return
    
    pusers = await get_variable("puser", {})
    if not pusers:
        return await message.reply_text("❌ **No premium users found.**")
        
    sent_count = 0
    now = datetime.now()
    
    for uid_str, expiry_date in pusers.items():
        time_left = expiry_date - now
        
        # যদি মেয়াদ ৩ দিন বা তার কম থাকে
        if timedelta(days=0) < time_left <= timedelta(days=3):
            try:
                days_left = time_left.days
                reminder_text = f"⚠️ **Pʀᴇᴍɪᴜᴍ Exᴘɪʀʏ Nᴏᴛɪᴄᴇ**\n\nDear User, your Premium Subscription will expire in **{days_left} days**!\n\nPlease renew your subscription to continue enjoying Ad-free direct downloads. 👑"
                
                await client.send_message(chat_id=int(uid_str), text=reminder_text)
                sent_count += 1
                await asyncio.sleep(1)
            except:
                pass
                
    await message.reply_text(f"✅ **Done!** Sent expiry reminders to `{sent_count}` premium users.")

# ==========================================
# 🔔 4. ADMIN LOG CHANNEL SYSTEM (Feature 11 & 43)
# ==========================================
@Bot.on_message(filters.command("setlog") & filters.private)
async def set_log_channel(client: Client, message: Message):
    """বটের যাবতীয় ইম্পর্ট্যান্ট নোটিফিকেশন পাওয়ার জন্য একটি প্রাইভেট লগ চ্যানেল সেট করা"""
    if not await is_admin(message.from_user.id): return
    
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/setlog [Channel ID]`\nExample: `/setlog -100987654321`")
        
    try:
        log_channel_id = int(message.command[1])
        await set_variable("log_channel", log_channel_id)
        
        # লগ চ্যানেলে একটি টেস্ট মেসেজ পাঠানো
        await client.send_message(
            chat_id=log_channel_id, 
            text="✅ **Admin Log Channel Successfully Connected!**\nAll system alerts and ban notifications will be sent here."
        )
        await message.reply_text(f"✅ **Success!** Log channel set to `{log_channel_id}`.")
        
    except ValueError:
        await message.reply_text("❌ **Channel ID must be a number!**")
    except Exception as e:
        await message.reply_text(f"❌ **Make sure the bot is an admin in the log channel!**\nError: `{e}`")

