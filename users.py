import json
import os

from config import CHANNEL_ID
from database.database import user_data

def fetch_user_ids():
    try:
        user_docs = user_data.find()
        user_ids = [doc["_id"] for doc in user_docs]
        print(f"Fetched {len(user_ids)} user IDs.") 
        return user_ids
    except Exception as e:
        print(f"Error fetching user IDs: {e}")
        return []

def save_user_ids_to_json(user_ids):
    try:
        with open("UsersBackup.json", "w") as f:
            json.dump(user_ids, f)
        print("User IDs saved to UsersBackup.json")
    except Exception as e:
        print(f"Error saving user IDs to JSON file: {e}")

# 🔥 FIX 2: Client Error Fixed and Cleanup added
async def send_user_ids_to_channel(client):
    user_ids = fetch_user_ids()
    if user_ids:
        save_user_ids_to_json(user_ids)

        try:
            with open("UsersBackup.json", "rb") as f:
                print("Attempting to send document...")
                await client.send_document(CHANNEL_ID, f, caption="📂 **Users Database Backup**")
                print(f"Document sent successfully to channel: {CHANNEL_ID}")
        except Exception as e:
            print(f"Error sending file to channel: {e}")
        finally:
            if os.path.exists("UsersBackup.json"):
                os.remove("UsersBackup.json") # মেসেজ পাঠানোর পর ফাইল ডিলিট করে দেবে
    else:
        print("No user IDs to send.")

async def handle_senduser_command(client, message):
    try:
        wait_msg = await message.reply_text("⏳ Processing User Backup...")
        await send_user_ids_to_channel(client)
        await wait_msg.edit_text("✅ **User Database Backup sent to the Database Channel successfully!**")
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")
