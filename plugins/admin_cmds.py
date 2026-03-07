# (©) Advanced Admin Commands & Database Export System
import os
import csv
from pyrogram import Client, filters
from pyrogram.types import Message

from bot import Bot
from database.database import get_variable, user_data

# ==========================================
# 🛡️ ADMIN CHECKER
# ==========================================
async def is_admin(user_id: int):
    """চেক করবে মেসেজ দেওয়া ব্যক্তি অ্যাডমিন কি না"""
    admins = await get_variable("admin", [])
    return user_id in admins

# ==========================================
# 🔍 1. USER SEARCH & PROFILE (Feature 24)
# ==========================================
@Bot.on_message(filters.command("search") & filters.private)
async def search_user(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/search [User ID]`")
        
    try:
        target_id = int(message.command[1])
        user = user_data.find_one({"_id": target_id})
        
        if not user:
            return await message.reply_text("❌ **User not found in database!**")
            
        join_date = user.get("join_date").strftime("%Y-%m-%d %H:%M:%S") if user.get("join_date") else "Unknown"
        status = "🔴 BANNED" if user.get("is_banned") else "🟢 ACTIVE"
        
        text = f"""
👤 **Uꜱᴇʀ Dᴀᴛᴀʙᴀꜱᴇ Pʀᴏғɪʟᴇ**

**UID:** `{target_id}`
**Sᴛᴀᴛᴜꜱ:** {status}
**Bᴀʟᴀɴᴄᴇ:** `৳ {round(user.get('balance', 0.0), 3)}`
**Vɪᴇᴡꜱ:** `{user.get('views', 0)}`
**Rᴇғᴇʀʀᴀʟꜱ:** `{user.get('referral_count', 0)}`
**Wᴀʀɴɪɴɢꜱ:** `{user.get('warnings', 0)}/3`
**Jᴏɪɴ Dᴀᴛᴇ:** `{join_date}`
"""
        await message.reply_text(text)
    except ValueError:
        await message.reply_text("❌ **Invalid User ID format!**")

# ==========================================
# 💰 2. MANUAL BALANCE EDIT (Feature 22)
# ==========================================
@Bot.on_message(filters.command(["addbalance", "removebalance"]) & filters.private)
async def edit_balance(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    
    if len(message.command) < 3:
        return await message.reply_text("❌ **Usage:** `/addbalance [User ID] [Amount]`")
        
    try:
        target_id = int(message.command[1])
        amount = float(message.command[2])
        
        user = user_data.find_one({"_id": target_id})
        if not user:
            return await message.reply_text("❌ **User not found!**")
            
        if message.command[0] == "addbalance":
            user_data.update_one({"_id": target_id}, {"$inc": {"balance": amount}})
            action = "Added to"
        else:
            user_data.update_one({"_id": target_id}, {"$inc": {"balance": -amount}})
            action = "Deducted from"
            
        await message.reply_text(f"✅ **Successfully {action} user {target_id}.**\nAmount: `৳ {amount}`")
    except ValueError:
        await message.reply_text("❌ **Invalid ID or Amount!**")

# ==========================================
# 🚫 3. BAN / UNBAN SYSTEM (Feature 45)
# ==========================================
@Bot.on_message(filters.command(["ban", "unban"]) & filters.private)
async def toggle_ban(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    
    if len(message.command) < 2:
        return await message.reply_text("❌ **Usage:** `/ban [User ID]` or `/unban [User ID]`")
        
    try:
        target_id = int(message.command[1])
        
        if message.command[0] == "ban":
            user_data.update_one({"_id": target_id}, {"$set": {"is_banned": True}})
            await message.reply_text(f"🚫 **User {target_id} has been BANNED.**")
        else:
            user_data.update_one({"_id": target_id}, {"$set": {"is_banned": False, "warnings": 0}})
            await message.reply_text(f"✅ **User {target_id} has been UNBANNED.**")
    except ValueError:
        await message.reply_text("❌ **Invalid User ID!**")

# ==========================================
# 📊 4. DATABASE EXPORT TO CSV (Feature 26)
# ==========================================
@Bot.on_message(filters.command("export") & filters.private)
async def export_database(client: Client, message: Message):
    if not await is_admin(message.from_user.id): return
    
    wait_msg = await message.reply_text("⏳ **Exporting database to CSV... please wait.**")
    
    try:
        file_name = "Users_Database_Export.csv"
        users = user_data.find()
        
        with open(file_name, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["User ID", "Balance", "Views", "Referrals", "Banned", "Join Date"])
            
            for user in users:
                join_date = user.get("join_date").strftime("%Y-%m-%d") if user.get("join_date") else "N/A"
                writer.writerow([
                    user["_id"], 
                    round(user.get("balance", 0.0), 3), 
                    user.get("views", 0), 
                    user.get("referral_count", 0), 
                    user.get("is_banned", False),
                    join_date
                ])
                
        await wait_msg.delete()
        await message.reply_document(
            document=file_name,
            caption="📊 **Here is your complete Database Export (CSV).**\nYou can open this in Microsoft Excel or Google Sheets."
        )
        os.remove(file_name) # ফাইল পাঠানো শেষে সার্ভার থেকে মুছে ফেলা হবে
        
    except Exception as e:
        await wait_msg.edit_text(f"❌ **Failed to export database:** `{e}`")

