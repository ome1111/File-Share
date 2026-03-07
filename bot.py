# (©) Secured by Developer
import asyncio
import os
import sys
from datetime import datetime

import pyrogram.utils
from aiohttp import web
from pyrogram import Client
from pyrogram.enums import ParseMode

# 🔥 FIX: basic.loop ইম্পোর্ট সরিয়ে ফেলা হয়েছে কারণ ফাইলটি আর নেই
from config import (
    API_HASH,
    APP_ID,
    CHANNEL_ID,
    LOGGER,
    OWNER_ID,
    PORT,
    TG_BOT_TOKEN,
    TG_BOT_WORKERS,
)
from database.database import get_variable, set_variable
from plugins import web_server

pyrogram.utils.MIN_CHANNEL_ID = -1002475424150

name = """
░█████╗░███╗░░██╗██╗███╗░░░███╗███████╗  ██╗░░██╗██╗░░░██╗███████╗
██╔══██╗████╗░██║██║████╗░████║██╔════╝  ╚██╗██╔╝╚██╗░██╔╝╚════██║
███████║██╔██╗██║██║██╔████╔██║█████╗░░  ░╚███╔╝░░╚████╔╝░░░███╔═╝
██╔══██║██║╚████║██║██║╚██╔╝██║██╔══╝░░  ░██╔██╗░░░╚██╔╝░░░██╔══╝░
██║░░██║██║░╚███║██║██║░╚═╝░██║███████╗  ██╔╝╚██╗░░██║░░░███████╗
╚═╝░░╚═╝╚═╝░░╚══╝╚═╝╚═╝░░░░░╚═╝╚══════╝  ╚═╝░░╚═╝░░╚═╝░░░╚══════╝
"""

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN,
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = self.me
        self.uptime = datetime.now()

        # 📂 Database Channel Setup (ফাইল রিকোয়েস্টের জন্য মাস্ট)
        try:
            self.db_channel = await self.get_chat(CHANNEL_ID)
        except Exception as e:
            self.LOGGER(__name__).error(f"Make sure bot is admin in DB Channel! Error: {e}")
            sys.exit(1)

        # 🛡️ সিকিউরিটি এবং অ্যাডমিন অটো-সেটআপ
        owner_str = await get_variable("owner", "")
        owner = [int(x.strip()) for x in owner_str.split() if x.strip().isdigit()]
        
        if OWNER_ID and OWNER_ID not in owner:
            owner.append(OWNER_ID)

        admin = await get_variable("admin", [])
        if not admin:
            admin = []

        updated_admin = False
        for owner_id in owner:
            if owner_id not in admin:
                admin.append(owner_id)
                updated_admin = True

        await set_variable("owner", " ".join(map(str, owner)))
        if updated_admin:
            await set_variable("admin", admin)

        # 🌐 Web Server Start (অ্যাডমিন প্যানেল ও শর্টলিংক ভিউয়ের জন্য)
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

        # 🔥 FIX: api_switch_loop টাস্কটি সরিয়ে ফেলা হয়েছে
        
        print(name)
        self.LOGGER(__name__).info(f"Bot started as {usr_bot_me.first_name}")
        self.LOGGER(__name__).info(f"Owner ID is secured and set to: {OWNER_ID}")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")
