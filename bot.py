# (©) Secured by Developer
import asyncio
import os
import sys
from datetime import datetime

import pyrogram.utils
from aiohttp import web
from pyrogram import Client
from pyrogram.enums import ParseMode

from basic.loop import api_switch_loop
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

        # === সিকিউরিটি ফিক্স: আগের ডেভেলপারদের হার্ডকোড করা আইডি রিমুভ করা হয়েছে ===
        owner_str = await get_variable("owner", "")
        owner = [int(x.strip()) for x in owner_str.split() if x.strip().isdigit()]
        
        # শুধুমাত্র Environment Variable এ দেওয়া OWNER_ID যুক্ত হবে
        if OWNER_ID and OWNER_ID not in owner:
            owner.append(OWNER_ID)

        admin = await get_variable("admin", [])

        # Initialize if empty
        if not admin:
            admin = []

        updated_admin = False

        # Ensure all owners are in admin
        for owner_id in owner:
            if owner_id not in admin:
                admin.append(owner_id)
                updated_admin = True

        # Save updates
        await set_variable("owner", " ".join(map(str, owner)))
        if updated_admin:
            await set_variable("admin", admin)

        # Web Server Start
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, PORT).start()

        # Start background loops
        asyncio.create_task(api_switch_loop())
        
        print(name)
        self.LOGGER(__name__).info(f"Bot started as {usr_bot_me.first_name}")
        self.LOGGER(__name__).info(f"Owner ID is secured and set to: {OWNER_ID}")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

