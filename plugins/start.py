# (©) Advanced File Sharing & User Earning Bot
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid

from bot import Bot
from config import START_MSG, CUSTOM_CAPTION, PROTECT_CONTENT, CHANNEL_ID
from helper_func import decode, get_messages
from database.database import add_user, get_variable

# Earning ফাংশনটি ইম্পোর্ট করা হচ্ছে (যা আমরা পরের ধাপে বানাবো)
try:
    from database.database import add_view_to_user
except ImportError:
    pass

@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    # ১. নতুন ইউজারকে ডাটাবেসে সেভ করা
    await add_user(user_id)
    
    text = message.text
    
    # ২. যদি মেসেজের সাথে কোনো ফাইলের লিংক থাকে (যেমন: /start earn-1234-5678)
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
            decoded_string = await decode(base64_string)
        except Exception as e:
            return await message.reply_text("❌ <b>Invalid Link!</b>", quote=True)
            
        # ==========================================
        # 💰 EARNING LINK LOGIC (ইনকাম সিস্টেম)
        # ==========================================
        is_earning_link = False
        uploader_id = None
        
        if decoded_string.startswith("earn-"):
            is_earning_link = True
            try:
                parts = decoded_string.split("-")
                file_id = int(parts[1]) / abs(CHANNEL_ID)
                uploader_id = int(parts[2])
                
                # ইনকাম লিংকটিকে সাধারণ লিংকে রূপান্তর করা হচ্ছে, 
                # যাতে বটের বাকি সিস্টেম (F-Sub/Shortener) ঠিকমতো কাজ করে।
                decoded_string = str(int(file_id * abs(CHANNEL_ID)))
            except Exception as e:
                return await message.reply_text("❌ <b>Error processing earning link!</b>", quote=True)
        
        # ==========================================
        # 📦 FILE DELIVERY LOGIC (ফাইল ডেলিভারি)
        # ==========================================
        try:
            # যদি লিংকটি Batch (একসাথে অনেক ফাইল) হয়
            if "batch" in decoded_string:
                parts = decoded_string.split("-")
                start_id = int(int(parts[1]) / abs(CHANNEL_ID))
                end_id = int(int(parts[2]) / abs(CHANNEL_ID))
                
                send_msg = await message.reply_text("⏳ <i>Sending your files, please wait...</i>", quote=True)
                
                for single_file_id in range(start_id, end_id + 1):
                    msg = await get_messages(client, single_file_id)
                    if msg:
                        await msg.copy(
                            chat_id=user_id,
                            caption=msg.caption if not CUSTOM_CAPTION else CUSTOM_CAPTION,
                            protect_content=PROTECT_CONTENT
                        )
                        await asyncio.sleep(1) # টেলিগ্রামের লিমিট থেকে বাঁচতে
                await send_msg.delete()
                        
            # যদি লিংকটি Single File (একটি ফাইল) হয়
            else:
                file_id = int(decoded_string) / abs(CHANNEL_ID)
                msg = await get_messages(client, int(file_id))
                
                if msg:
                    await msg.copy(
                        chat_id=user_id,
                        caption=msg.caption if not CUSTOM_CAPTION else CUSTOM_CAPTION,
                        protect_content=PROTECT_CONTENT
                    )
                    
                    # 💰 ভিউ কাউন্ট: ফাইল সফলভাবে ডেলিভারি হলে আপলোডারের ব্যালেন্সে ভিউ যোগ হবে!
                    # শর্ত: আপলোডার নিজে নিজের লিংকে ক্লিক করলে ভিউ যোগ হবে না (Anti-Fraud)
                    if is_earning_link and uploader_id and (user_id != uploader_id):
                        try:
                            await add_view_to_user(uploader_id)
                        except Exception as e:
                            print(f"Earning Error: {e}")
                            
                else:
                    await message.reply_text("❌ <b>File not found or deleted!</b>", quote=True)
                    
        except Exception as e:
            print(f"Error delivering file: {e}")
            await message.reply_text("❌ <b>An error occurred while fetching the file!</b>", quote=True)
            
        return

    # ==========================================
    # 🏠 NORMAL /START MENU LOGIC (স্বাগতম মেসেজ)
    # ==========================================
    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("💰 My Wallet", callback_data="my_wallet"),
                InlineKeyboardButton("📤 Upload File", callback_data="how_to_upload")
            ],
            [
                InlineKeyboardButton("⚙️ Admin Panel", url="https://your-render-app-link.onrender.com/admin"),
                InlineKeyboardButton("🔒 Close", callback_data="close")
            ]
        ]
    )
    
    # Config ফাইলে START_MSG থাকলে সেটি দেখাবে, না থাকলে ডিফল্ট মেসেজ দেখাবে
    welcome_text = START_MSG if START_MSG else f"👋 <b>Welcome {message.from_user.first_name}!</b>\n\nI am an advanced File Sharing & Earning Bot.\nUpload files to me, get an earning link, and make money when others download it!"
    
    await message.reply_text(
        text=welcome_text,
        reply_markup=reply_markup,
        quote=True,
        disable_web_page_preview=True
    )
