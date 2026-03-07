# (©) User Upload & Earning System - Step 1
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot import Bot
from config import CHANNEL_ID
from helper_func import encode

# এই হ্যান্ডলারটি ইউজারদের পাঠানো যেকোনো ডকুমেন্ট, ভিডিও, অডিও বা ছবি রিসিভ করবে
@Bot.on_message(filters.private & (filters.document | filters.video | filters.audio | filters.photo))
async def handle_user_upload(client: Client, message: Message):
    user_id = message.from_user.id
    
    reply_text = await message.reply_text("⏳ <i>Processing your file for earning link...</i>", quote=True)
    
    try:
        # ইউজারের ফাইলটি ডাটাবেস চ্যানেলে সেভ করা হচ্ছে
        post_message = await message.copy(
            chat_id=CHANNEL_ID, 
            disable_notification=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.value)
        post_message = await message.copy(
            chat_id=CHANNEL_ID, 
            disable_notification=True
        )
    except Exception as e:
        print(f"Error copying user file: {e}")
        await reply_text.edit_text("❌ Something went wrong while processing your file.")
        return

    # ফাইলের মেসেজ আইডি এবং ডাটাবেস আইডি গুণ করে সিকিউর করা হচ্ছে
    converted_id = post_message.id * abs(CHANNEL_ID)
    
    # নতুন সিস্টেমের লিংক ফরম্যাট: earn-{file_id}-{user_id}
    # এতে ফাইলের সাথে আপলোডারের আইডিও যুক্ত থাকছে, ফলে কার ফাইল কে দেখলো তা ট্র্যাক করা যাবে!
    string = f"earn-{converted_id}-{user_id}"
    base64_string = await encode(string)
    
    link = f"https://t.me/{client.username}?start={base64_string}"

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔁 Share & Earn URL", url=f"https://telegram.me/share/url?url={link}"
                )
            ]
        ]
    )

    await reply_text.edit(
        f"🎉 **File Uploaded Successfully!**\n\n"
        f"🔗 **Your Earning Link:**\n<code>{link}</code>\n\n"
        f"💸 <i>Share this link with your friends or channel. Every time someone accesses this file, you will earn views and money!</i>",
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )
