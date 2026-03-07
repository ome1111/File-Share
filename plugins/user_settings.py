# (©) Advanced User Settings, Thumbnail & File Rename System
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from bot import Bot
from database.database import set_user_thumbnail, get_user_thumbnail, set_user_language, get_user_language

# ==========================================
# 🖼️ 1. CUSTOM THUMBNAIL SYSTEM (Feature 15)
# ==========================================
@Bot.on_message(filters.private & filters.photo)
async def save_thumbnail(client: Client, message: Message):
    """ইউজার কোনো ছবি পাঠালে সেটি তার কাস্টম থাম্বনেইল হিসেবে সেভ হবে"""
    user_id = message.from_user.id
    file_id = message.photo.file_id
    
    await set_user_thumbnail(user_id, file_id)
    await message.reply_text(
        "✅ **Custom Thumbnail Saved!**\n\nThis image will be used for your renamed files.",
        quote=True
    )

@Bot.on_message(filters.private & filters.command("delthumb"))
async def delete_thumbnail(client: Client, message: Message):
    """থাম্বনেইল ডিলিট করার কমান্ড"""
    await set_user_thumbnail(message.from_user.id, None)
    await message.reply_text("🗑️ **Custom Thumbnail Deleted successfully!**", quote=True)

# ==========================================
# ✍️ 2. FILE RENAME SYSTEM (Feature 14)
# ==========================================
@Bot.on_message(filters.private & filters.command("rename"))
async def rename_file(client: Client, message: Message):
    """ফাইল রিনেম করার লজিক (Reply to a file with /rename new_name)"""
    user_id = message.from_user.id
    reply_msg = message.reply_to_message
    
    if not reply_msg or not (reply_msg.document or reply_msg.video or reply_msg.audio):
        return await message.reply_text("❌ **Reply to a file/video to rename it!**\nExample: `/rename My_New_Movie_Name.mkv`")
        
    if len(message.command) < 2:
        return await message.reply_text("❌ **Provide a new name!**\nExample: `/rename My_New_Movie_Name.mkv`")

    new_name = message.text.split(" ", 1)[1]
    wait_msg = await message.reply_text("⏳ **Downloading file to server... please wait!**")
    
    try:
        # File Download (Render সার্ভারে টেম্পোরারি সেভ হবে)
        file_path = await client.download_media(message.reply_to_message)
        
        await wait_msg.edit_text("⏳ **Uploading with new name...**")
        
        # ইউজারের কাস্টম থাম্বনেইল ডাটাবেস থেকে নেওয়া
        thumb_id = await get_user_thumbnail(user_id)
        thumb_path = None
        if thumb_id:
            thumb_path = await client.download_media(thumb_id)

        # File Upload with new name
        if reply_msg.video or str(file_path).endswith((".mkv", ".mp4", ".webm")):
            await client.send_video(
                chat_id=user_id,
                video=file_path,
                file_name=new_name,
                thumb=thumb_path,
                caption=f"**{new_name}**"
            )
        else:
            await client.send_document(
                chat_id=user_id,
                document=file_path,
                file_name=new_name,
                thumb=thumb_path,
                caption=f"**{new_name}**"
            )
            
        await wait_msg.delete()
        
        # ক্লিনআপ (সার্ভার থেকে ডিলিট করা যাতে স্টোরেজ ফুল না হয়)
        os.remove(file_path)
        if thumb_path:
            os.remove(thumb_path)
            
    except Exception as e:
        await wait_msg.edit_text(f"❌ **Error occurred:** `{e}`")

# ==========================================
# ⚙️ 3. MULTI-LANGUAGE & SETTINGS (Feature 33)
# ==========================================
@Bot.on_message(filters.private & filters.command("settings"))
async def settings_menu(client: Client, message: Message):
    """ইউজার সেটিংস মেনু (Language)"""
    user_id = message.from_user.id
    current_lang = await get_user_language(user_id)
    
    lang_display = "English 🇬🇧" if current_lang == "en" else "Bengali 🇧🇩" if current_lang == "bn" else "Hindi 🇮🇳"
    
    text = f"⚙️ **Yᴏᴜʀ Sᴇᴛᴛɪɴɢꜱ Mᴇɴᴜ**\n\n🗣️ **Cᴜʀʀᴇɴᴛ Lᴀɴɢᴜᴀɢᴇ:** `{lang_display}`\n\n_Select your preferred language below:_"
    
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇬🇧 English", callback_data="set_lang_en"),
         InlineKeyboardButton("🇧🇩 বাংলা", callback_data="set_lang_bn"),
         InlineKeyboardButton("🇮🇳 हिन्दी", callback_data="set_lang_hi")],
        [InlineKeyboardButton("🔒 Close", callback_data="close")]
    ])
    
    await message.reply_text(text, reply_markup=reply_markup)

@Bot.on_callback_query(filters.regex(r"^set_lang_"))
async def change_language(client: Client, query: CallbackQuery):
    lang_code = query.data.split("_")[2]
    await set_user_language(query.from_user.id, lang_code)
    
    if lang_code == "bn":
        await query.answer("✅ ভাষা সফলভাবে পরিবর্তন করা হয়েছে!", show_alert=True)
        await query.message.edit_text("✅ আপনার ভাষা **বাংলা** সেট করা হয়েছে। (Note: Full bot translation will be applied soon!)")
    elif lang_code == "hi":
        await query.answer("✅ भाषा सफलतापूर्वक बदल दी गई!", show_alert=True)
        await query.message.edit_text("✅ आपकी भाषा **हिन्दी** सेट कर दी गई है।")
    else:
        await query.answer("✅ Language changed to English!", show_alert=True)
        await query.message.edit_text("✅ Your language has been set to **English**.")
