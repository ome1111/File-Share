import pymongo
from pymongo.errors import DuplicateKeyError

from data import DB_NAME, DB_URI

# Initialize MongoDB client
dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]
user_data = database["users"]
config_data = database["config"]


async def add_user(user_id: int):
    try:
        # ইনকাম সিস্টেমের জন্য নতুন ইউজার অ্যাড হওয়ার সময় views এবং balance জিরো (0) হিসেবে সেভ হবে
        user_data.insert_one({"_id": user_id, "views": 0, "balance": 0.0})
    except DuplicateKeyError:
        # ইউজার আগে থেকেই থাকলে কোনো এরর দেবে না
        pass
    except Exception as e:
        print(f"Error adding user {user_id}: {e}")


async def present_user(user_id: int):
    try:
        found = user_data.find_one({"_id": user_id})
        return bool(found)
    except Exception as e:
        print(f"Error finding user {user_id}: {e}")
        return False


async def full_userbase():
    try:
        user_docs = user_data.find()
        user_ids = [doc["_id"] for doc in user_docs]
        return user_ids
    except Exception as e:
        print(f"Error retrieving user base: {e}")
        return []


async def del_user(user_id: int):
    try:
        result = user_data.delete_one({"_id": user_id})

    except Exception as e:
        print(f"Error deleting user {user_id}: {e}")


async def set_variable(key: str, value):
    """Set a configuration variable in the database."""
    config_data.update_one(
        {"_id": key},
        {"$set": {"value": value}},  # Stores value directly, preserving type
        upsert=True,
    )


async def get_variable(key: str, default=None):
    """Retrieve a configuration variable from the database and fallback to default if missing or None."""

    if config_data is None:
        raise Exception("config_data collection is not initialized!")

    entry = config_data.find_one({"_id": key})
    if not entry:
        # Insert the key with default value (can be None or an actual default)
        config_data.insert_one({"_id": key, "value": default})
        return default

    value = entry.get("value", default)
    # Handle case when the value is None
    if value is None:
        return default
    return value


async def get_all_variables():
    """Retrieve all configuration variable keys and values from the database."""
    cursor = config_data.find({})
    variables = []
    for entry in cursor:  # Fixed to synchronous 'for' as pymongo cursor is sync
        variables.append((entry["_id"], entry["value"]))
    return variables


# =====================================================================
# 💰 NEW: USER EARNING SYSTEM FUNCTIONS (ইনকাম এবং ওয়ালেট সিস্টেম)
# =====================================================================

async def add_view_to_user(user_id: int):
    """ইউজারের লিংকে কেউ ক্লিক করে ফাইল রিসিভ করলে তার ভিউ এবং ব্যালেন্স যোগ হবে"""
    try:
        # ডাটাবেস (বা ওয়েব প্যানেল) থেকে CPM রেট বের করা। ডিফল্ট: 1000 ভিউতে 50 টাকা।
        cpm = await get_variable("cpm", 50.0) 
        earning_per_view = float(cpm) / 1000.0

        user_data.update_one(
            {"_id": user_id},
            {"$inc": {"views": 1, "balance": earning_per_view}},
            upsert=True
        )
    except Exception as e:
        print(f"Error adding view to user {user_id}: {e}")


async def get_user_wallet(user_id: int):
    """ইউজারের বর্তমান ভিউ এবং ব্যালেন্স চেক করার জন্য"""
    try:
        user = user_data.find_one({"_id": user_id})
        if user:
            return {
                "views": user.get("views", 0),
                "balance": round(user.get("balance", 0.0), 3) # ৩ দশমিক স্থান পর্যন্ত দেখাবে
            }
        return {"views": 0, "balance": 0.0}
    except Exception as e:
        print(f"Error getting wallet for {user_id}: {e}")
        return {"views": 0, "balance": 0.0}


async def reset_user_balance(user_id: int):
    """উইথড্র (টাকা তোলার) পর অ্যাডমিন যেন ইউজারের ব্যালেন্স জিরো করতে পারে"""
    try:
        user_data.update_one(
            {"_id": user_id},
            {"$set": {"balance": 0.0}}
        )
        return True
    except Exception as e:
        print(f"Error resetting balance for {user_id}: {e}")
        return False
