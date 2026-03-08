from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from bot import Bot
from helper_func import get_shortlink

# এটি যেকোনো মেসেজ চেক করবে যেটিতে http বা https আছে
@Bot.on_message(
    filters.private 
    & filters.text 
    & filters.regex(r"https?://") 
    & ~filters.command(["start", "users", "broadcast", "addfsub", "delfsub", "withdraw", "stats", "senduser"])
)
async def url_shortener_handler(client: Client, message: Message):
    """ইউজার কোনো বাইরের লিংক দিলে সেটি শর্ট করে দেবে"""
    
    # ইউজারের পাঠানো লিংকটি বের করা
    url = message.text.strip()
    user_id = message.from_user.id
    
    wait_msg = await message.reply_text("⏳ **Shortening your link...**", quote=True)
    
    try:
        # helper_func এর নতুন ফাংশন ব্যবহার করে লিংক শর্ট করা (user_id সহ)
        short_link = await get_shortlink(url, user_id=user_id)
        
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🔁 Share Earning Link", url=f"https://telegram.me/share/url?url={short_link}")]]
        )
        
        success_text = (
            "✅ **Link Shortened Successfully!**\n\n"
            f"🔗 **Your Link:** `{short_link}`\n\n"
            "💰 *Share this link with your friends. When they click and view the ad, you will earn money!*"
        )
        
        await wait_msg.edit_text(success_text, reply_markup=reply_markup, disable_web_page_preview=True)
        
    except Exception as e:
        await wait_msg.edit_text(f"❌ **Failed to shorten link!** Error: {e}")
