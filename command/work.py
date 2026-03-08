import random
from datetime import datetime, timedelta

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import LOGGER, images
from database.database import add_user, get_variable, present_user, set_variable

log = LOGGER(__name__)

# ==========================================
# 🚀 FSUB HELPER (ক্লিন ডাটাবেস লজিক)
# ==========================================
async def get_fsub_list():
    """ডাটাবেস থেকে স্পন্সর চ্যানেলের লিস্ট আনবে"""
    fsub = await get_variable("fsub", [])
    if isinstance(fsub, str): 
        # পুরোনো কোনো ডাটা থাকলে সেটাকে লিস্ট করে নেবে
        return [int(x.strip()) for x in fsub.split() if x.strip()]
    return fsub

# ==========================================
# 🛑 CHECK SUBSCRIPTION FOR COMMANDS
# ==========================================
async def not_subscribed(c, client, message, user_id=False):
    if not user_id:
        user_id = message.from_user.id

    fsub_channels = await get_fsub_list()
    if not fsub_channels:
        return False # কোনো স্পন্সর চ্যানেল না থাকলে সোজা ফাইল দিয়ে দেবে

    for channel in fsub_channels:
        try:
            user = await client.get_chat_member(channel, user_id)
            if user.status in {ChatMemberStatus.BANNED, ChatMemberStatus.LEFT}:
                await force_subs(client, message)
                return True
        except UserNotParticipant:
            await force_subs(client, message)
            return True
        except Exception as e:
            log.error(f"Skipping fsub check for {channel}: {e}")
            continue

    return False

async def subscribed(_, client, message, q=False):
    user_id = message.from_user.id if not q else q.from_user.id
    fsub_channels = await get_fsub_list()
    
    if not fsub_channels:
        return True

    for channel in fsub_channels:
        try:
            user = await client.get_chat_member(channel, user_id)
            if user.status in {ChatMemberStatus.BANNED, ChatMemberStatus.LEFT}:
                return False
        except UserNotParticipant:
            return False
        except Exception:
            continue
    return True

# ==========================================
# 📢 SEND FORCE SUB MESSAGE & BUTTONS
# ==========================================
async def force_subs(client, message):
    IMAGE_URL = random.choice(images) if images else None
    fsub_channels = await get_fsub_list()
    user_id = message.from_user.id

    if not await present_user(user_id):
        await add_user(user_id)

    not_joined_channels = []
    for channel in fsub_channels:
        try:
            user = await client.get_chat_member(channel, user_id)
            if user.status in {ChatMemberStatus.BANNED, ChatMemberStatus.LEFT}:
                not_joined_channels.append(channel)
        except UserNotParticipant:
            not_joined_channels.append(channel)
        except Exception:
            pass

    buttons = []
    for idx, channel in enumerate(not_joined_channels, 1):
        try:
            chat = await client.get_chat(channel)
            try:
                # অটোমেটিক ইনভাইট লিংক বানাবে
                invite = await client.create_chat_invite_link(
                    chat_id=channel, expire_date=datetime.now() + timedelta(minutes=10)
                )
                link = invite.invite_link
            except Exception:
                link = chat.invite_link or f"https://t.me/{chat.username}"
            
            name = chat.title or f"Sponsor Channel {idx}"
            buttons.append([InlineKeyboardButton(text=f"📢 ᴊᴏɪɴ {name}", url=link)])
        except Exception:
            pass

    # আগের মেসেজ থেকে start প্যারামিটার (যেমন: get-12345) বের করা
    text = message.text if hasattr(message, "text") and message.text else ""
    string = text.split(" ", 1)[1] if len(text.split()) > 1 else ""

    buttons.append([InlineKeyboardButton(text="✅ ɪ ʜᴀᴠᴇ ᴊᴏɪɴᴇᴅ", callback_data=f"check_subscription{string}")])

    caption = f"❌ **Access Denied!**\n\nHello {message.from_user.mention}, you **MUST** join all our sponsor channels below to use this bot.\n\nAfter joining, click the **'I Have Joined'** button."

    if IMAGE_URL:
        await message.reply_photo(photo=IMAGE_URL, caption=caption, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await message.reply_text(text=caption, reply_markup=InlineKeyboardMarkup(buttons))

# ==========================================
# ✅ CALLBACK QUERY CHECK (I HAVE JOINED)
# ==========================================
async def check_subscription(client, callback_query: CallbackQuery, string):
    user_id = callback_query.from_user.id
    fsub_channels = await get_fsub_list()
    
    not_joined_channels = []
    for channel in fsub_channels:
        try:
            user = await client.get_chat_member(channel, user_id)
            if user.status in {ChatMemberStatus.BANNED, ChatMemberStatus.LEFT}:
                not_joined_channels.append(channel)
        except UserNotParticipant:
            not_joined_channels.append(channel)
        except Exception:
            pass

    if not not_joined_channels:
        # ইউজার সব চ্যানেলে জয়েন করেছে
        new_text = "**✅ You have joined all the required channels. Thank you!**"
        key = None
        if string:
            new_text = "<blockquote><b><i>✅ Subscription Verified! Click below to get your file 💠</i></b></blockquote>"
            key = [InlineKeyboardButton(text="🚀 ɢᴇᴛ ғɪʟᴇ ɴᴏᴡ", url=f"https://t.me/{client.me.username}?start={string}")]
        
        if callback_query.message.caption != new_text:
            await callback_query.message.edit_caption(
                caption=new_text,
                reply_markup=InlineKeyboardMarkup([key]) if key else None,
            )
        return

    # ইউজার এখনো জয়েন করেনি
    await callback_query.answer("⚠️ You haven't joined all channels yet! Please join them first.", show_alert=True)

# ==========================================
# ⚙️ ADMIN VARIABLE SETTER
# ==========================================
async def varsa(client, message):
    try:
        parts = message.text.split(maxsplit=1)
        if len(parts) < 2:
            return await message.reply_text("Usage: `/Vars variable-name - variable-value`")

        _, data = parts
        if " - " in data:
            variable_name, variable_value = data.split(" - ", 1)
        else:
            return await message.reply_text("Usage: `/Vars variable-name - variable-value`")

        variable_name = variable_name.strip()
        variable_value = variable_value.strip()
        
        if variable_name == "admin":
            admin = await get_variable("admin", [])
            if not isinstance(admin, list):
                admin = []
            try:
                admin_value = int(variable_value)
                if admin_value not in admin:
                    admin.append(admin_value)
                await set_variable("admin", admin)
            except ValueError:
                return await message.reply_text("Admin value must be an integer.")
        else:
            await set_variable(variable_name, variable_value)
            
        await message.reply_text(f"✅ Variable '{variable_name}' set to '{variable_value}'")
    except Exception as e:
        await message.reply_text(f"❌ An error occurred: {e}")
