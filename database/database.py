import pymongo
from pymongo.errors import DuplicateKeyError
from datetime import datetime

from data import DB_NAME, DB_URI

# Initialize MongoDB client
dbclient = pymongo.MongoClient(DB_URI)
database = dbclient[DB_NAME]
user_data = database["users"]
config_data = database["config"]
withdraw_data = database["withdrawals"] # Feature 3, 21: Withdrawal History & Panel

# =====================================================================
# 🛠️ CORE & USER MANAGEMENT (Upgraded with Referral & Ban System)
# =====================================================================

async def add_user(user_id: int, invited_by: int = 0):
    """নতুন ইউজার যুক্ত করা এবং রেফারেল ট্র্যাক করা (Feature 1, 33, 15)"""
    try:
        user_data.insert_one({
            "_id": user_id, 
            "views": 0, 
            "balance": 0.0,
            "invited_by": invited_by,
            "referral_count": 0,
            "warnings": 0,         # Feature 10: Auto-ban spammers
            "is_banned": False,    # Feature 8: Fake view detection
            "lang": "en",          # Feature 33: Multi-language Support
            "thumbnail": None,     # Feature 15: Custom Thumbnail
            "join_date": datetime.now()
        })
        
        # যদি কারও রেফারেল লিংকে জয়েন করে থাকে
        if invited_by != 0 and invited_by != user_id:
            user_data.update_one({"_id": invited_by}, {"$inc": {"referral_count": 1}})
            
    except DuplicateKeyError:
        pass
    except Exception as e:
        print(f"Error adding user {user_id}: {e}")

async def present_user(user_id: int):
    try:
        found = user_data.find_one({"_id": user_id})
        return bool(found)
    except Exception as e:
        return False

async def get_user(user_id: int):
    """ইউজারের প্রোফাইল ডাটা বের করার জন্য (Feature 34: User Status Menu)"""
    try:
        return user_data.find_one({"_id": user_id})
    except:
        return None

async def full_userbase():
    try:
        user_docs = user_data.find()
        return [doc["_id"] for doc in user_docs]
    except Exception as e:
        return []

async def del_user(user_id: int):
    try:
        user_data.delete_one({"_id": user_id})
    except Exception as e:
        pass

# =====================================================================
# ⚙️ CONFIG & VARIABLES MANAGEMENT
# =====================================================================

async def set_variable(key: str, value):
    config_data.update_one({"_id": key}, {"$set": {"value": value}}, upsert=True)

async def get_variable(key: str, default=None):
    if config_data is None:
        raise Exception("config_data collection is not initialized!")
    entry = config_data.find_one({"_id": key})
    if not entry:
        config_data.insert_one({"_id": key, "value": default})
        return default
    value = entry.get("value", default)
    return default if value is None else value

async def get_all_variables():
    cursor = config_data.find({})
    variables = []
    for entry in cursor:
        variables.append((entry["_id"], entry["value"]))
    return variables

# =====================================================================
# 💰 EARNING, WALLET & REFERRAL SYSTEM
# =====================================================================

async def add_view_to_user(user_id: int):
    """ভিউ কাউন্ট এবং রেফারেল কমিশন (Feature 1)"""
    try:
        user = user_data.find_one({"_id": user_id})
        if not user or user.get("is_banned", False): return # ব্যান ইউজার টাকা পাবে না

        cpm = float(await get_variable("cpm", 50.0))
        earning_per_view = cpm / 1000.0

        # মেইন ইউজারের টাকা অ্যাড করা
        user_data.update_one({"_id": user_id}, {"$inc": {"views": 1, "balance": earning_per_view}})

        # Feature 1: রেফারেল কমিশন (যিনি ইনভাইট করেছেন তিনি ৫% পাবেন)
        invited_by = user.get("invited_by", 0)
        if invited_by != 0:
            referral_bonus = earning_per_view * 0.05
            user_data.update_one({"_id": invited_by}, {"$inc": {"balance": referral_bonus}})

    except Exception as e:
        print(f"Error adding view: {e}")

async def get_user_wallet(user_id: int):
    try:
        user = user_data.find_one({"_id": user_id})
        if user:
            return {
                "views": user.get("views", 0),
                "balance": round(user.get("balance", 0.0), 3),
                "referrals": user.get("referral_count", 0)
            }
        return {"views": 0, "balance": 0.0, "referrals": 0}
    except Exception:
        return {"views": 0, "balance": 0.0, "referrals": 0}

async def reset_user_balance(user_id: int):
    try:
        user_data.update_one({"_id": user_id}, {"$set": {"balance": 0.0}})
        return True
    except:
        return False

# =====================================================================
# 🏆 LEADERBOARD & WITHDRAWAL HISTORY (Feature 3, 6, 21)
# =====================================================================

async def get_top_earners(limit: int = 10):
    """Feature 6: টপ ১০ আর্নার বের করা"""
    try:
        top_users = user_data.find({"is_banned": False}).sort("balance", -1).limit(limit)
        return list(top_users)
    except Exception:
        return []

async def add_withdrawal_request(user_id: int, amount: float, method: str, details: str):
    """Feature 3 & 21: উইথড্র রিকোয়েস্ট ডাটাবেসে সেভ করা"""
    try:
        withdraw_data.insert_one({
            "user_id": user_id,
            "amount": amount,
            "method": method,
            "details": details,
            "status": "Pending",
            "date": datetime.now()
        })
        # টাকা কাটার লজিক
        user_data.update_one({"_id": user_id}, {"$inc": {"balance": -amount}})
        return True
    except:
        return False

async def get_withdrawal_history(user_id: int):
    """ইউজারের উইথড্র হিস্ট্রি বের করা"""
    try:
        history = withdraw_data.find({"user_id": user_id}).sort("date", -1).limit(5)
        return list(history)
    except:
        return []

# =====================================================================
# 🛡️ ANTI-FRAUD & SECURITY (Feature 8, 10)
# =====================================================================

async def warn_user(user_id: int):
    """ফেক ক্লিক করলে ওয়ার্নিং দেওয়া, ৩ বার হলে ব্যান করা"""
    try:
        user = user_data.find_one({"_id": user_id})
        if user:
            warnings = user.get("warnings", 0) + 1
            if warnings >= 3:
                user_data.update_one({"_id": user_id}, {"$set": {"warnings": warnings, "is_banned": True}})
                return "BANNED"
            else:
                user_data.update_one({"_id": user_id}, {"$set": {"warnings": warnings}})
                return f"WARNED_{warnings}"
    except:
        return "ERROR"

# =====================================================================
# 🎨 CUSTOMIZATIONS (Feature 15, 33)
# =====================================================================

async def set_user_thumbnail(user_id: int, file_id: str):
    user_data.update_one({"_id": user_id}, {"$set": {"thumbnail": file_id}})

async def get_user_thumbnail(user_id: int):
    user = user_data.find_one({"_id": user_id})
    return user.get("thumbnail", None) if user else None

async def set_user_language(user_id: int, lang_code: str):
    user_data.update_one({"_id": user_id}, {"$set": {"lang": lang_code}})

async def get_user_language(user_id: int):
    user = user_data.find_one({"_id": user_id})
    return user.get("lang", "en") if user else "en"

