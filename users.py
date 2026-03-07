import json
import pymongo
import os

from bot import Bot  
from data import DB_URI, DB_NAME
from config import CHANNEL_ID

# MongoDB setup (Secured)
dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]
user_data = database["users"]

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

async def send_user_ids_to_channel():
    user_ids = fetch_user_ids()
    if user_ids:
        save_user_ids_to_json(user_ids)

        try:
            async with Bot:
                with open("UsersBackup.json", "rb") as f:
                    print("Attempting to send document...")
                    response = await Bot.send_document(CHANNEL_ID, f)
                    print(f"Document sent successfully to channel: {CHANNEL_ID}")
            print("User IDs sent to channel successfully.")
        except Exception as e:
            print(f"Error sending file to channel: {e}")
    else:
        print("No user IDs to send.")

async def handle_senduser_command(client, message):
    try:
        await send_user_ids_to_channel()
        await message.reply("✅ User IDs backup has been successfully sent to the Database Channel.")
    except Exception as e:
        await message.reply(f"❌ An error occurred: {e}")
