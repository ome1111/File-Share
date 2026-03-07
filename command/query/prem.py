import pyrogram.utils
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import LOGGER
from database.database import get_variable

pyrogram.utils.MIN_CHANNEL_ID = -1009147483647
pyrogram.utils.MAX_CHANNEL_ID = -1000000000000
log = LOGGER(__name__)

async def prem(client, query):
    log.info("Premium function triggered")
    
    # ওয়েব প্যানেল (ডাটাবেস) থেকে আপনার সেট করা UPI ID নিয়ে আসবে
    upi_id = await get_variable("upi_id", "Not Set (Contact Admin)")

    text = f"""🌟 <b>Premium Access</b> 🌟<b>
</b><blockquote expandable><b><i>🔥 Elevate your experience with Premium Access! 🔥</i></b></blockquote>

<b>💸 ᴘʀᴇᴍɪᴜᴍ ᴘʟᴀɴs:
➥ ₹10 - </b>1 ᴅᴀʏ ᴀᴄᴄᴇss <b>
➥ ₹50 - </b>2 ᴡᴇᴇᴋs ᴀᴄᴄᴇss<b> 
➥ ₹100 - </b>1 ᴍᴏɴᴛʜ ᴀᴄᴄᴇss<b>
➥ ₹699 - </b>1 ʏᴇᴀʀ ᴀᴄᴄᴇss

<blockquote expandable>🛍 <b>ʜᴏᴡ ᴛᴏ ᴘᴜʀᴄʜᴀsᴇ ᴘʀᴇᴍɪᴜᴍ -</b>

💫 <b>sᴄᴀɴ</b> ᴛʜᴇ ǫʀ ᴄᴏᴅᴇ Ꭺʙᴏvᴇ.
💫 <b>sᴇɴᴅ</b> ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ᴀᴍᴏᴜɴᴛ ᴀᴄᴄᴏʀᴅɪɴɢ ᴛᴏ ᴛʜᴇ ᴘʟᴀɴ ʏᴏᴜ ᴡᴀɴᴛ.
💫 <b>ʀᴇᴘᴏʀᴛ</b> ʏᴏᴜʀ ᴘᴀʏᴍᴇɴᴛ sᴄʀᴇᴇɴsʜᴏᴛ ᴛᴏ ᴛʜᴇ ᴏᴡɴᴇʀ ᴜsɪɴɢ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ!                                              
</blockquote>📨 𝚄𝙿𝙸 𝙸𝙳: <code>{upi_id}</code>"""

    # নিচে পেমেন্ট প্রুফ পাঠানোর বাটনের লিংক (আপনি চাইলে URL পরিবর্তন করতে পারেন)
    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("💳 Sᴇɴᴅ Pᴀʏᴍᴇɴᴛ Sᴄʀᴇᴇɴsʜᴏᴛ", url="https://t.me/YourUsername")],
            [InlineKeyboardButton("🔒 Cʟᴏsᴇ", callback_data="close")]
        ]
    )

    await query.message.edit_text(
        text=text,
        reply_markup=keyboard,
        disable_web_page_preview=True
    )
