# (©) Crypto Payments, Premium Badges, API Rotation & Server Logs
import os
import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from bot import Bot
from database.database import get_variable, user_data
from plugins.premium_admin import check_premium, is_admin

# ==========================================
# 💳 1. CRYPTO PAYMENT SYSTEM (Feature 31)
# ==========================================
@Bot.on_message(filters.command("buypremium") & filters.private)
async def buy_premium_crypto(client: Client, message: Message):
    """ইউজারদের ক্রিপ্টোকারেন্সি বা অন্যান্য মাধ্যমে প্রিমিয়াম কেনার অপশন"""
    text = """
👑 **Uᴘɢʀᴀᴅᴇ ᴛᴏ Pʀᴇᴍɪᴜᴍ!**

Get rid of annoying shortener ads and enjoy direct downloads forever! ⚡️

**🪙 Pʀɪᴄɪɴɢ Pʟᴀɴꜱ:**
• 1 Month: `$2` (or ৳200)
• 3 Months: `$5` (or ৳500)
• Lifetime: `$15` (or ৳1500)

**🏦 Aᴄᴄᴇᴘᴛᴇᴅ Pᴀʏᴍᴇɴᴛꜱ:**
• **Binance Pay ID:** `123456789`
• **USDT (TRC20):** `Txxxxxxxxxxxxxxxxxxxxxxxxxxxx`
• **bKash/Nagad:** Send message to Admin.

_After payment, send a screenshot or TxID to the Admin below to activate your premium badge!_
"""
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("👨‍💻 Contact Admin", url="https://t.me/YourUsername")],
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ])
    
    await message.reply_text(text, reply_markup=reply_markup)

# ==========================================
# 🌟 2. PREMIUM BADGE & PROFILE (Feature 32)
# ==========================================
@Bot.on_message(filters.command("profile") & filters.private)
async def user_profile_badge(client: Client, message: Message):
    """ইউজারের প্রোফাইল কমান্ড যেখানে প্রিমিয়াম ব্যাজ শো করবে"""
    user_id = message.from_user.id
    user = user_data.find_one({"_id": user_id})
    
    if not user:
        return await message.reply_text("❌ **Profile not found! Type /start first.**")
        
    is_prem = await check_premium(user_id)
    badge = "🌟 **PREMIUM MEMBER** 👑" if is_prem else "👤 **NORMAL USER**"
    
    join_date = user.get("join_date").strftime("%d %b, %Y") if user.get("join_date") else "Unknown"
    balance = round(user.get("balance", 0.0), 3)
    
    text = f"""
{badge}

**Nᴀᴍᴇ:** {message.from_user.first_name}
**UID:** `{user_id}`
**Bᴀʟᴀɴᴄᴇ:** `৳ {balance}`
**Tᴏᴛᴀʟ Vɪᴇᴡꜱ:** `{user.get('views', 0)}`
**Jᴏɪɴ Dᴀᴛᴇ:** `{join_date}`

_Use /buypremium to upgrade your account!_
"""
    await message.reply_text(text)

# ==========================================
# 🖥️ 3. LIVE TERMINAL LOGS (Feature 25)
# ==========================================
@Bot.on_message(filters.command("logs") & filters.private)
async def get_server_logs(client: Client, message: Message):
    """Render সার্ভারে না ঢুকেও টেলিগ্রাম থেকে বটের লাইভ এরর লগ দেখা"""
    if not await is_admin(message.from_user.id): return
    
    wait_msg = await message.reply_text("⏳ **Fetching live server logs...**")
    
    log_file = "bot.log" # Make sure your bot creates this log file in config.py
    
    if not os.path.exists(log_file):
        return await wait_msg.edit_text("❌ **Log file not found!** Make sure logging to file is enabled.")
        
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # শেষের ৪০টি লাইনের লগ দেখাবে
            last_lines = "".join(lines[-40:])
            
        if len(last_lines) > 4000:
            last_lines = last_lines[-4000:] # টেলিগ্রামের মেসেজ লিমিট
            
        await wait_msg.edit_text(f"🖥️ **Sᴇʀᴠᴇʀ Tᴇʀᴍɪɴᴀʟ Lᴏɢꜱ (Last 40 lines):**\n\n`{last_lines}`")
    except Exception as e:
        await wait_msg.edit_text(f"❌ **Error reading logs:** `{e}`")

# ==========================================
# 🔄 4. SHORTENER API ROTATION (Feature 44)
# ==========================================
async def get_rotated_shortlink(url: str):
    """
    এই ফাংশনটি শর্টনারের API টোকেন রোটেট করবে। 
    যদি Token 1 কাজ না করে বা লিমিট শেষ হয়ে যায়, অটোমেটিক Token 2 ব্যবহার করবে!
    (এটি helper_func.py এর get_shortlink() কে রিপ্লেস করার জন্য ডিজাইন করা)
    """
    token_1 = await get_variable("token_1", "")
    token_2 = await get_variable("token_2", "")
    shortener_url = await get_variable("shortener_domain", "https://api.shareus.io") # Default Domain
    
    async def fetch_link(token):
        api_url = f"{shortener_url}/api?api={token}&url={url}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=5) as response:
                    data = await response.json()
                    if "shortenedUrl" in data:
                        return data["shortenedUrl"]
                    elif "url" in data:
                        return data["url"]
        except Exception as e:
            print(f"API Error with token {token[:5]}: {e}")
        return None

    # প্রথমে টোকেন ১ দিয়ে ট্রাই করবে
    if token_1:
        short_link = await fetch_link(token_1)
        if short_link: return short_link
        
    # টোকেন ১ ফেইল করলে টোকেন ২ দিয়ে ট্রাই করবে (API Rotation)
    if token_2:
        print("Token 1 failed. Rotating to Token 2...")
        short_link = await fetch_link(token_2)
        if short_link: return short_link
        
    # যদি দুটোই ফেইল করে, তবে মেইন অরিজিনাল লিংকটাই দিয়ে দেবে যাতে বটের কাজ বন্ধ না হয়!
    return url

