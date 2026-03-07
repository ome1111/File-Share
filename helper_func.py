# (©) Custom Link Generator & Helper Functions
import base64
import asyncio
import os
import random
import string
import re
from datetime import datetime
from pyrogram import Client
from pyrogram.errors import FloodWait

# ডাটাবেস কানেকশন ইম্পোর্ট
from database.database import database

# শর্টলিংকের জন্য তৈরি করা নতুন কালেকশন
shortlinks_db = database["shortlinks"]

async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    base64_string = (base64_bytes.decode("ascii")).strip("=")
    return base64_string

async def decode(base64_string):
    base64_string = base64_string.strip("=")
    base64_bytes = (base64_string + "=" * (-len(base64_string) % 4)).encode("ascii")
    string_bytes = base64.urlsafe_b64decode(base64_bytes) 
    string = string_bytes.decode("ascii")
    return string

async def get_messages(client, message_ids):
    messages = []
    total_messages = 0
    while total_messages != len(message_ids):
        temb_ids = message_ids[total_messages:total_messages+200]
        try:
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except FloodWait as e:
            await asyncio.sleep(e.value)
            msgs = await client.get_messages(
                chat_id=client.db_channel.id,
                message_ids=temb_ids
            )
        except:
            pass
        total_messages += len(temb_ids)
        messages.extend(msgs)
    return messages

# ==========================================
# 🛠️ MESSAGE ID GETTER
# ==========================================
def get_message_id(client, message):
    if message.forward_from_chat:
        if message.forward_from_chat.id == client.db_channel.id:
            return message.forward_from_message_id
    elif message.forward_sender_name:
        return 0
    elif message.text:
        pattern = "https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern, message.text)
        if not matches:
            return 0
        channel_id = matches.group(1)
        msg_id = int(matches.group(2))
        if channel_id.isdigit():
            if f"-100{channel_id}" == str(client.db_channel.id):
                return msg_id
        else:
            if channel_id == client.db_channel.username:
                return msg_id
    return 0

# ==========================================
# 🚀 YOUR CUSTOM SHORTLINK GENERATOR (Fixed)
# ==========================================
async def get_shortlink(url: str):
    """
    এই ফাংশনটি এখন থেকে আর Shareus ব্যবহার করবে না!
    এটি আপনার ডাটাবেসে লিংক সেভ করে আপনার ওয়েবসাইটের লিংক ইউজারকে দেবে।
    """
    # আপনার বটের আসল ওয়েবসাইটের ডোমেইন
    YOUR_DOMAIN = "https://file-share-1hlu.onrender.com"
    
    # একটি র‍্যান্ডম ৬ অক্ষরের ইউনিক আইডি তৈরি করা
    link_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    
    # 🔥 FIX: এখানে await যোগ করা হয়েছে। await ছাড়া Async DB তে ডাটা সেভ হয় না।
    try:
        await shortlinks_db.insert_one({
            "_id": link_id,
            "title": "Secure File Download",
            "destination_url": url,  # মেইন টেলিগ্রাম ফাইলের লিংক
            "image_url": "https://cdn-icons-png.flaticon.com/512/285/285032.png",
            "views": 0,
            "status": "active",
            "created_at": datetime.now()
        })
    except Exception as e:
        print(f"Error saving shortlink: {e}")
        return url # এরর হলে অরিজিনাল লিংকই পাঠিয়ে দেবে যাতে ইউজার ফাইল পায়
    
    # আপনার ওয়েবসাইটের ভিউ পেজের ফাইনাল লিংক রিটার্ন করা
    return f"{YOUR_DOMAIN}/view/{link_id}"
