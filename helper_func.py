# (©) Custom Link Generator & Helper Functions
import base64
import asyncio
import os
import random
import string
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
# 🚀 YOUR CUSTOM SHORTLINK GENERATOR
# ==========================================
async def get_shortlink(url: str):
    """
    এই ফাংশনটি এখন থেকে আর Shareus ব্যবহার করবে না!
    এটি আপনার ডাটাবেসে লিংক সেভ করে আপনার ওয়েবসাইটের লিংক ইউজারকে দেবে।
    """
    
    # ১. আপনার বটের ওয়েবসাইটের ডোমেইন
    # Render অটোমেটিক তার ডোমেইন এখানে বসিয়ে নেবে। যদি লোকালহোস্টে টেস্ট করেন, তবে নিচের "https://..." এর জায়গায় আপনার বটের আসল লিংকটি বসিয়ে দেবেন।
    YOUR_DOMAIN = os.environ.get("RENDER_EXTERNAL_URL", "https://your-app-name.onrender.com")
    
    # ২. একটি র‍্যান্ডম ৬ অক্ষরের ইউনিক আইডি তৈরি করা (যেমন: aB3x9Q)
    link_id = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    
    # ৩. ডাটাবেসে লিংকের সব তথ্য সেভ করা
    shortlinks_db.insert_one({
        "_id": link_id,
        "title": "Secure File Download",
        "destination_url": url,  # মেইন টেলিগ্রাম ফাইলের লিংক
        "image_url": "https://cdn-icons-png.flaticon.com/512/285/285032.png", # আপনার পেজে দেখানোর জন্য সুন্দর একটি আইকন
        "views": 0,
        "status": "active"
    })
    
    # ৪. আপনার ওয়েবসাইটের ভিউ পেজের ফাইনাল লিংক রিটার্ন করা
    return f"{YOUR_DOMAIN}/view/{link_id}"

