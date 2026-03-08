from pyrogram import Client, filters
from database.database import get_variable, set_variable
from bot import Bot

@Bot.on_message(filters.command("addfsub") & filters.private)
async def add_fsub(client, message):
    admin = await get_variable("admin", [])
    if message.from_user.id not in admin: return
    
    if len(message.command) < 2:
        return await message.reply("⚠️ Usage: `/addfsub -100xxxxxxx`")
    
    try:
        channel_id = int(message.command[1])
        fsub_list = await get_variable("fsub", [])
        if channel_id in fsub_list:
            return await message.reply("⚠️ Channel is already in the FSub list.")
        
        chat = await client.get_chat(channel_id) # বটের অ্যাডমিন থাকা মাস্ট
        fsub_list.append(channel_id)
        await set_variable("fsub", fsub_list)
        await message.reply(f"✅ Successfully added **{chat.title}** to Multi-FSub list!")
    except Exception as e:
        await message.reply(f"❌ Error: Make sure the bot is ADMIN in that channel! ({e})")

@Bot.on_message(filters.command("delfsub") & filters.private)
async def del_fsub(client, message):
    admin = await get_variable("admin", [])
    if message.from_user.id not in admin: return
    
    if len(message.command) < 2:
        return await message.reply("⚠️ Usage: `/delfsub -100xxxxxxx`")
    
    try:
        channel_id = int(message.command[1])
        fsub_list = await get_variable("fsub", [])
        if channel_id in fsub_list:
            fsub_list.remove(channel_id)
            await set_variable("fsub", fsub_list)
            await message.reply("✅ Channel removed from FSub list.")
        else:
            await message.reply("❌ Channel not found in list.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")
