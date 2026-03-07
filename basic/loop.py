import asyncio
from datetime import datetime, timedelta
import pytz

from database.database import get_variable, set_variable

# Indian timezone
IST = pytz.timezone("Asia/Kolkata")

def time_until_next_trigger(now):
    """
    Returns timedelta until next noon or midnight.
    """
    today = now.date()

    # Today's noon and next midnight
    noon = IST.localize(
        datetime.combine(today, datetime.min.time()) + timedelta(hours=12)
    )
    midnight = IST.localize(
        datetime.combine(today + timedelta(days=1), datetime.min.time())
    )

    return noon - now if now < noon else midnight - now


async def api_switch_loop():
    while True:
        now = datetime.now(IST)
        wait_duration = time_until_next_trigger(now)

        print(f"Sleeping for {wait_duration} until next switch.")
        await asyncio.sleep(wait_duration.total_seconds())

        current_api = await get_variable("api", "")
        
        # ডাটাবেস (ওয়েব প্যানেল) থেকে লেটেস্ট টোকেনগুলো নিয়ে আসবে
        token_1 = await get_variable("token_1", "")
        token_2 = await get_variable("token_2", "")

        # যদি প্যানেলে টোকেন বসানো না থাকে, তবে এরর এড়াতে লুপটি স্কিপ করবে
        if not token_1 or not token_2:
            print("Tokens are not set in the Web Admin Panel. Skipping switch.")
            continue

        # টোকেন সুইচিং লজিক
        if current_api == token_1:
            await set_variable("api", token_2)
            print("Successfully Switched API to Token 2")
        else:
            await set_variable("api", token_1)
            print("Successfully Switched API to Token 1")

