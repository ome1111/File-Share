import asyncio
from datetime import datetime
from pymongo.errors import DuplicateKeyError
import motor.motor_asyncio

from data import DB_NAME, DB_URI

# Initialize Async MongoDB client (Motor)
dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]
user_data = database["users"]
config_data = database["config"]
withdraw_data = database["withdrawals"]
reward_logs = database["reward_logs"] # 🔥 Anti-Fraud Tracking

# =====================================================================
# 🛠️ CORE & USER MANAGEMENT
# =====================================================================

async def add_user(user_id: int, invited_by: int = 0):
    """নতুন ইউজার যুক্ত করা এবং রেফারেল ট্র্যাক করা"""
    try:
        await user_data.insert_one({
            "_id": user_id, 
            "views": 0, 
            "balance": 0.0,
            "invited_by": invited_by,
            "referral_count": 0,
            "warnings": 0,         
            "is_banned": False,    
            "lang": "en",          
            "thumbnail": None,     
            "join_date": datetime.now()
        })
        
        # যদি কারও রেফারেল লিংকে জয়েন করে থাকে
        if invited_by != 0 and invited_by != user_id:
            await user_data.update_one({"_id": invited_by}, {"$inc": {"referral_count": 1}})
            
    except DuplicateKeyError:
        pass
    except Exception as e:
        print(f"Error adding user {user_id}: {e}")

async def present_user(user_id: int):
    try:
        found = await user_data.find_one({"_id": user_id})
        return bool(found)
    except Exception as e:
        return False

async def get_user(user_id: int):
    try:
        return await user_data.find_one({"_id": user_id})
    except:
        return None

async def full_userbase():
    try:
        cursor = user_data.find({})
        user_docs = await cursor.to_list(length=None)
        return [doc["_id"] for doc in user_docs]
    except Exception as e:
        return []

async def del_user(user_id: int):
    try:
        await user_data.delete_one({"_id": user_id})
    except Exception as e:
        pass

# =====================================================================
# ⚙️ CONFIG & VARIABLES MANAGEMENT
# =====================================================================

async def set_variable(key: str, value):
    await config_data.update_one({"_id": key}, {"$set": {"value": value}}, upsert=True)

async def get_variable(key: str, default=None):
    if config_data is None:
        raise Exception("config_data collection is not initialized!")
    entry = await config_data.find_one({"_id": key})
    if not entry:
        await config_data.insert_one({"_id": key, "value": default})
        return default
    value = entry.get("value", default)
    return default if value is None else value

async def get_all_variables():
    cursor = config_data.find({})
    variables = []
    async for entry in cursor:
        variables.append((entry["_id"], entry["value"]))
    return variables

# =====================================================================
# 💰 EARNING, WALLET & REFERRAL SYSTEM
# =====================================================================

async def add_view_to_user(user_id: int):
    """ভিউ কাউন্ট এবং রেফারেল কমিশন (Feature 1)"""
    try:
        user = await user_data.find_one({"_id": int(user_id)})
        if not user or user.get("is_banned", False): return

        cpm = float(await get_variable("cpm", 50.0))
        earning_per_view = cpm / 1000.0

        await user_data.update_one({"_id": int(user_id)}, {"$inc": {"views": 1, "balance": earning_per_view}})

        invited_by = user.get("invited_by", 0)
        if invited_by != 0:
            referral_bonus = earning_per_view * 0.05
            await user_data.update_one({"_id": invited_by}, {"$inc": {"balance": referral_bonus}})

    except Exception as e:
        print(f"Error adding view: {e}")

async def get_user_wallet(user_id: int):
    try:
        user = await user_data.find_one({"_id": user_id})
        if user:
            ref_count = await user_data.count_documents({"invited_by": int(user_id)})
            return {
                "views": user.get("views", 0),
                "balance": round(user.get("balance", 0.0), 3),
                "referrals": ref_count
            }
        return {"views": 0, "balance": 0.0, "referrals": 0}
    except Exception:
        return {"views": 0, "balance": 0.0, "referrals": 0}

async def reset_user_balance(user_id: int):
    try:
        await user_data.update_one({"_id": user_id}, {"$set": {"balance": 0.0}})
        return True
    except:
        return False

# =====================================================================
# 🏆 LEADERBOARD & WITHDRAWAL HISTORY
# =====================================================================

async def get_top_earners(limit: int = 10):
    try:
        cursor = user_data.find({"is_banned": False}).sort("balance", -1).limit(limit)
        return await cursor.to_list(length=limit)
    except Exception:
        return []

async def add_withdrawal_request(user_id: int, amount: float, method: str, details: str):
    try:
        await withdraw_data.insert_one({
            "user_id": user_id,
            "amount": amount,
            "method": method,
            "details": details,
            "status": "Pending",
            "date": datetime.now()
        })
        await user_data.update_one({"_id": user_id}, {"$inc": {"balance": -amount}})
        return True
    except:
        return False

async def get_withdrawal_history(user_id: int):
    try:
        cursor = withdraw_data.find({"user_id": user_id}).sort("date", -1).limit(5)
        return await cursor.to_list(length=5)
    except:
        return []

# =====================================================================
# 🛡️ ANTI-FRAUD & SECURITY
# =====================================================================

async def warn_user(user_id: int):
    try:
        user = await user_data.find_one({"_id": user_id})
        if user:
            warnings = user.get("warnings", 0) + 1
            if warnings >= 3:
                await user_data.update_one({"_id": user_id}, {"$set": {"warnings": warnings, "is_banned": True}})
                return "BANNED"
            else:
                await user_data.update_one({"_id": user_id}, {"$set": {"warnings": warnings}})
                return f"WARNED_{warnings}"
    except:
        return "ERROR"

async def check_and_add_reward(downloader_id: int, uploader_id: int, file_id: str):
    """চেক করবে এই ইউজারটি আগে কখনো এই ফাইলটি দেখেছে কি না। (1 User = 1 View)"""
    try:
        # নিজের ফাইলে নিজে ক্লিক করলে টাকা পাবে না
        if int(downloader_id) == int(uploader_id):
            return False
            
        # চেক করবে সে আগে এই ফাইলের জন্য টাকা দিয়েছে কি না
        existing = await reward_logs.find_one({
            "downloader_id": int(downloader_id),
            "file_id": str(file_id)
        })
        
        if existing:
            return False 
            
        # নতুন ক্লিক হলে ডাটাবেসে সেভ করে রাখবে
        await reward_logs.insert_one({
            "downloader_id": int(downloader_id),
            "uploader_id": int(uploader_id),
            "file_id": str(file_id),
            "timestamp": datetime.now()
        })
        
        # সবকিছু ঠিক থাকলে ইউজারের ব্যালেন্সে টাকা যোগ করবে
        await add_view_to_user(uploader_id)
        return True
        
    except Exception as e:
        print(f"Anti-Fraud Error: {e}")
        return False

# =====================================================================
# 🎨 CUSTOMIZATIONS
# =====================================================================

async def set_user_thumbnail(user_id: int, file_id: str):
    await user_data.update_one({"_id": user_id}, {"$set": {"thumbnail": file_id}})

async def get_user_thumbnail(user_id: int):
    user = await user_data.find_one({"_id": user_id})
    return user.get("thumbnail", None) if user else None

async def set_user_language(user_id: int, lang_code: str):
    await user_data.update_one({"_id": user_id}, {"$set": {"lang": lang_code}})

async def get_user_language(user_id: int):
    user = await user_data.find_one({"_id": user_id})
    return user.get("lang", "en") if user else "en"
