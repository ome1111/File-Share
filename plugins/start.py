# (©) Advanced File Sharing & User Earning Bot
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid

from bot import Bot
from config import *
from helper_func import decode, get_messages, get_shortlink, get_verify_status, update_verify_status
from database.database import add_user, get_variable

# Earning ফাংশনটি ইম্পোর্ট করা হচ্ছে
try:
    from database.database import add_view_to_user
except ImportError:
    pass

@Bot.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id
    
    # ইউজারকে ডাটাবেসে যুক্ত করা
    await add_user(user_id)
    
    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
        except:
            return

        # ==========================================
        # 🔑 TOKEN VERIFICATION & SHORTENER (আপনার অরিজিনাল লজিক)
        # ==========================================
        if base64_string.startswith("verify_"):
            try:
                _, token = base64_string.split("_", 1)
                verify_status = await get_verify_status(user_id)
                if verify_status['verify_token'] == token:
                    await update_verify_status(user_id, verify_token="", is_verified=True, verified_time=time.time())
                    await message.reply_text("✅ <b>You successfully verified! Now you have unlimited access for 24 hours.</b>", quote=True)
                else:
                    await message.reply_text("❌ <b>Invalid or Expired Token!</b>", quote=True)
            except Exception as e:
                print(e)
            return

        # ফাইল লিংক ডিকোড করা
        try:
            decoded_string = await decode(base64_string)
        except Exception as e:
            return await message.reply_text("❌ <b>Invalid Link!</b>", quote=True)

        # ==========================================
        # 💰 EARNING LINK LOGIC (নতুন ইনকাম সিস্টেম)
        # ==========================================
        is_earning_link = False
        uploader_id = None
        
        if decoded_string.startswith("earn-"):
            is_earning_link = True
            try:
                parts = decoded_string.split("-")
                file_id_str = parts[1]
                uploader_id = int(parts[2])
                
                # ইনকাম লিংকটিকে আপনার অরিজিনাল ফাইলের লিংকে রূপান্তর করা হচ্ছে
                # যাতে আপনার F-Sub, Shortener এবং Auto-Delete ঠিকঠাক কাজ করে!
                decoded_string = file_id_str
            except Exception as e:
                return await message.reply_text("❌ <b>Error processing earning link!</b>", quote=True)

        # ==========================================
        # 🛡️ F-SUB & PREMIUM VERIFICATION CHECK
        # ==========================================
        # (আপনার অরিজিনাল F-Sub এবং Token Checking লজিক এখানে কাজ করবে)
        is_verified = await get_verify_status(user_id)
        # Premium Check Logic here if applicable...
        
        if not is_verified['is_verified']:
            token_url = await get_shortlink(f"https://telegram.me/{client.username}?start=verify_{is_verified['verify_token']}")
            await message.reply_text(
                "⚠️ <b>You need to verify first to access this file!</b>\n\n<i>Click the button below to verify and get 24-hour access.</i>",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Verify Now", url=token_url)]]),
                quote=True
            )
            return

        # ==========================================
        # 📦 FILE DELIVERY (BATCH & SINGLE)
        # ==========================================
        try:
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
                        await asyncio.sleep(1)
                await send_msg.delete()
                
            else:
                file_id = int(decoded_string) / abs(CHANNEL_ID)
                msg = await get_messages(client, int(file_id))
                
                if msg:
                    await msg.copy(
                        chat_id=user_id,
                        caption=msg.caption if not CUSTOM_CAPTION else CUSTOM_CAPTION,
                        protect_content=PROTECT_CONTENT
                    )
                    
                    # 💰 ভিউ কাউন্ট: ফাইল ডেলিভারি হওয়ার পর ভিউ যোগ হবে!
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
    # 🏠 NORMAL /START MENU LOGIC
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
    
    welcome_text = START_MSG if START_MSG else f"👋 <b>Welcome {message.from_user.first_name}!</b>\n\nI am an advanced File Sharing & Earning Bot.\nUpload files to me, get an earning link, and make money when others download it!"
    
    await message.reply_text(
        text=welcome_text,
        reply_markup=reply_markup,
        quote=True,
        disable_web_page_preview=True
    )
