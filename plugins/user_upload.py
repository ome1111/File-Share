# (©) User Upload & Earning System - Step 1 (Fixed & Secured)
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot import Bot
from config import CHANNEL_ID
# 🔥 FIX: get_shortlink ইম্পোর্ট করা হলো
from helper_func import encode, get_shortlink 

# এই হ্যান্ডলারটি ইউজারদের পাঠানো যেকোনো ডকুমেন্ট, ভিডিও, অডিও বা ছবি রিসিভ করবে
@Bot.on_message(
    filters.private 
    & (filters.document | filters.video | filters.audio | filters.photo)
    & ~filters.command(["start", "users", "broadcast", "addfsub", "delfsub", "withdraw", "stats", "senduser"])
)
async def handle_user_upload(client: Client, message: Message):
    user_id = message.from_user.id
    
    reply_text = await message.reply_text("⏳ <i>Processing your file for earning link...</i>", quote=True)
    
    try:
        # ইউজারের ফাইলটি ডাটাবেস চ্যানেলে সেভ করা হচ্ছে
        post_message = await message.copy(
            chat_id=client.db_channel.id, 
            disable_notification=True
        )
    except FloodWait as e:
        await asyncio.sleep(e.value if hasattr(e, 'value') else e.x)
        post_message = await message.copy(
            chat_id=client.db_channel.id, 
            disable_notification=True
        )
    except Exception as e:
        print(f"Error copying user file: {e}")
        await reply_text.edit_text("❌ Something went wrong while processing your file.")
        return

    # ফাইলের মেসেজ আইডি এবং ডাটাবেস আইডি গুণ করে সিকিউর করা হচ্ছে
    converted_id = post_message.id * abs(client.db_channel.id)
    
    # নতুন সিস্টেমের লিংক ফরম্যাট: earn-{file_id}-{user_id}
    string = f"earn-{converted_id}-{user_id}"
    base64_string = await encode(string)
    
    bot_username = client.me.username
    bot_link = f"https://t.me/{bot_username}?start={base64_string}"

    # 🔥 MASTER FIX: সরাসরি বটের লিংক না দিয়ে, ওয়েবসাইটের শর্টলিংক বানিয়ে দেওয়া হচ্ছে (user_id সহ!)
    short_link = await get_shortlink(bot_link, user_id=user_id)

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔁 Share Earning Link", url=f"https://telegram.me/share/url?url={short_link}"
                )
            ]
        ]
    )

    await reply_text.edit(
        f"🎉 **File Uploaded Successfully!**\n\n"
        f"🔗 **Your Earning Link:**\n`{short_link}`\n\n"
        f"💸 <i>Share this link with your friends. Every time someone clicks and views the ad, you will earn money!</i>",
        reply_markup=reply_markup,
        disable_web_page_preview=True,
    )
