# (©) Monetized Link Generator
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot import Bot
from config import CHANNEL_ID
from helper_func import encode, get_shortlink

@Bot.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def generate_earning_link(client: Client, message: Message):
    # ইউজার ফাইল দিলে প্রথমে এই মেসেজটি দেবে
    wait_msg = await message.reply_text("⏳ **Processing your file for earning link...**")
    
    try:
        # ১. ফাইলটি আপনার ডাটাবেস চ্যানেলে সেভ করবে
        forwarded_msg = await message.copy(chat_id=CHANNEL_ID)
        
        # ২. ফাইলের আইডি এবং ইউজারের আইডি বের করবে
        msg_id_multiplied = forwarded_msg.id * abs(CHANNEL_ID)
        user_id = message.from_user.id
        
        # ৩. ইনকাম সিস্টেমের জন্য স্পেশাল স্ট্রিং তৈরি করবে (earn-fileid-userid)
        raw_string = f"earn-{msg_id_multiplied}-{user_id}"
        
        # ৪. কোডটিকে এনকোড করবে
        encoded_string = await encode(raw_string)
        
        # ৫. বটের অরিজিনাল লিংক তৈরি করবে
        bot_username = client.me.username
        bot_link = f"https://t.me/{bot_username}?start={encoded_string}"
        
        # ৬. আপনার ওয়েবসাইটের অ্যাড-পেজের শর্টলিংক জেনারেট করবে
        earning_link = await get_shortlink(bot_link)
        
        # ফাইলের নাম বের করা (সুন্দর করে দেখানোর জন্য)
        file_name = "File"
        if message.document: file_name = message.document.file_name
        elif message.video: file_name = message.video.file_name or "Video"
        elif message.audio: file_name = message.audio.file_name or "Audio"
        
        # ৭. ইউজারকে ফাইনাল ইনকাম লিংক দিয়ে দেবে
        text = f"""
✅ **Yᴏᴜʀ Eᴀʀɴɪɴɢ Lɪɴᴋ is Rᴇᴀᴅʏ!**

📁 **Fɪʟᴇ:** `{file_name}`
🔗 **Lɪɴᴋ:** `{earning_link}`

_Share this link everywhere! When someone downloads from this link, your wallet balance will increase automatically. 💸_
"""
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔁 Share Link", url=f"https://telegram.me/share/url?url={earning_link}")]
        ])
        
        await wait_msg.edit_text(text, reply_markup=reply_markup, disable_web_page_preview=True)
        
    except Exception as e:
        # যদি কোনো এরর হয়, তাহলে আর আটকে থাকবে না, সরাসরি এরর মেসেজ দেখাবে
        await wait_msg.edit_text(f"❌ **Error occurred:** `{e}`\n\n_Make sure your CHANNEL_ID is correctly set in Render environment variables._")
