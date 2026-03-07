# (©)Codexbotz
# Modified for Advanced Web Admin Panel & Earning System

import os
import json
import asyncio
from aiohttp import web
from bson.objectid import ObjectId

# এখানে আমরা bot ইম্পোর্ট করবো না, যাতে Circular Import Error না আসে!
from database.database import get_variable, set_variable, full_userbase, withdraw_data, user_data

routes = web.RouteTableDef()

# আপনার ওয়েব প্যানেলের লগইন পাসওয়ার্ড
WEB_ADMIN_PASS = os.environ.get("WEB_ADMIN_PASS", "admin123")

def check_auth(request):
    """চেক করবে ইউজার সঠিক পাসওয়ার্ড দিয়ে লগইন করেছে কি না"""
    auth_header = request.headers.get('Authorization')
    if auth_header == f"Bearer {WEB_ADMIN_PASS}":
        return True
    return False

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    """মেইন লিংকে গেলে বট যে জীবিত আছে তা দেখাবে"""
    return web.json_response({"status": "running", "message": "File Sharing & Earning Bot is Alive!"})

@routes.get("/admin")
async def admin_panel(request):
    """/admin লিংকে গেলে admin.html পেজটি শো করবে"""
    try:
        with open("admin.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return web.Response(text=html_content, content_type="text/html")
    except FileNotFoundError:
        return web.Response(text="<h1>Error 404: admin.html file not found!</h1><p>Please upload admin.html in the root folder.</p>", status=404, content_type="text/html")

@routes.post("/api/login")
async def api_login(request):
    """ওয়েব প্যানেলের লগইন রিকোয়েস্ট হ্যান্ডেল করবে"""
    try:
        data = await request.json()
        password = data.get("password", "")
        if password == WEB_ADMIN_PASS:
            return web.json_response({"success": True, "token": WEB_ADMIN_PASS})
        return web.json_response({"success": False, "error": "ভুল পাসওয়ার্ড! আবার চেষ্টা করুন।"}, status=401)
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)

@routes.get("/api/stats")
async def api_stats(request):
    """ড্যাশবোর্ডের জন্য ডাটাবেস থেকে লাইভ ডাটা পাঠাবে"""
    if not check_auth(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    users = await full_userbase()
    total_users = len(users)
    
    # ডাটাবেস থেকে সকল সেটিং ভ্যালুগুলো বের করা
    token_1 = await get_variable("token_1", "")
    token_2 = await get_variable("token_2", "")
    upi_id = await get_variable("upi_id", "")
    cpm = await get_variable("cpm", 50.0)
    
    # নতুন বটের সেটিংসগুলো
    del_timer = await get_variable("del_timer", 0)
    start_msg = await get_variable("START_MSG", "")
    fsub_channels = await get_variable("fsub_channels", [])
    
    return web.json_response({
        "total_users": total_users,
        "token_1": token_1,
        "token_2": token_2,
        "upi_id": upi_id,
        "cpm": cpm,
        "del_timer": del_timer,
        "START_MSG": start_msg,
        "fsub_channels": fsub_channels
    })

@routes.post("/api/update")
async def api_update(request):
    """ওয়েব প্যানেল থেকে পাঠানো নতুন সেটিং ডাটাবেসে সেভ করবে"""
    if not check_auth(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        key = data.get("key")
        value = data.get("value")
        
        if key and value is not None:
            if key in ["cpm"]:
                value = float(value)
            elif key in ["del_timer"]:
                value = int(value)
                
            await set_variable(key, value)
            return web.json_response({"success": True, "message": f"{key} successfully updated!"})
        return web.json_response({"success": False, "error": "Invalid data format."}, status=400)
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)

# ==========================================
# 💸 WITHDRAWAL REQUEST APIs
# ==========================================

@routes.get("/api/withdrawals")
async def api_get_withdrawals(request):
    if not check_auth(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        cursor = withdraw_data.find({"status": "Pending"}).sort("date", -1)
        requests = []
        for req in cursor:
            requests.append({
                "_id": str(req["_id"]),
                "user_id": req["user_id"],
                "amount": req["amount"],
                "method": req["method"],
                "details": req["details"],
                "date": req["date"].strftime("%d %b, %Y")
            })
        return web.json_response({"success": True, "requests": requests})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)

@routes.post("/api/withdraw_action")
async def api_withdraw_action(request):
    if not check_auth(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        req_id = data.get("request_id")
        action = data.get("action")
        user_id = data.get("user_id")
        amount = float(data.get("amount", 0))
        
        withdraw_data.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": action}})
        
        if action == "Rejected":
            user_data.update_one({"_id": int(user_id)}, {"$inc": {"balance": amount}})
            
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)

# ==========================================
# 👥 NEW: USER MANAGEMENT APIs
# ==========================================

@routes.post("/api/user_action")
async def api_user_action(request):
    """ওয়েব প্যানেল থেকে ইউজারকে সার্চ, ব্যালেন্স এডিট বা ব্যান করার জন্য"""
    if not check_auth(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
        
    try:
        data = await request.json()
        action = data.get("action")
        user_id = int(data.get("user_id", 0))
        amount = float(data.get("amount", 0.0))
        
        if not user_id:
            return web.json_response({"success": False, "error": "Invalid User ID"})
            
        user = user_data.find_one({"_id": user_id})
        
        if action == "search":
            if not user:
                return web.json_response({"success": False, "error": "User not found!"})
            return web.json_response({
                "success": True,
                "user": {
                    "balance": round(user.get("balance", 0.0), 3),
                    "views": user.get("views", 0),
                    "is_banned": user.get("is_banned", False)
                }
            })
            
        elif action == "add":
            user_data.update_one({"_id": user_id}, {"$inc": {"balance": amount}})
            return web.json_response({"success": True})
            
        elif action == "deduct":
            user_data.update_one({"_id": user_id}, {"$inc": {"balance": -amount}})
            return web.json_response({"success": True})
            
        elif action == "ban":
            user_data.update_one({"_id": user_id}, {"$set": {"is_banned": True}})
            return web.json_response({"success": True})
            
        elif action == "unban":
            user_data.update_one({"_id": user_id}, {"$set": {"is_banned": False, "warnings": 0}})
            return web.json_response({"success": True})
            
        return web.json_response({"success": False, "error": "Unknown Action"})
        
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)

# ==========================================
# 📢 NEW: WEB BROADCAST API
# ==========================================

@routes.post("/api/web_broadcast")
async def api_web_broadcast(request):
    """ওয়েব প্যানেল থেকে পাঠানো মেসেজ সকল ইউজারের কাছে ব্রডকাস্ট করবে"""
    if not check_auth(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
        
    try:
        data = await request.json()
        text = data.get("text")
        
        if not text:
            return web.json_response({"success": False, "error": "Message is empty!"})
            
        # ব্যাকগ্রাউন্ডে ব্রডকাস্ট চালানোর জন্য টাস্ক
        async def run_broadcast():
            # 🔥 Circular Import এরর ফিক্স করার জন্য Bot কে এখানে লোকালি ইম্পোর্ট করা হলো!
            from bot import Bot 
            
            users = await full_userbase()
            for uid in users:
                try:
                    await Bot.send_message(chat_id=uid, text=text, disable_web_page_preview=True)
                    await asyncio.sleep(0.5) # FloodWait এড়ানোর জন্য
                except Exception:
                    pass # ব্লক করা ইউজারদের ইগনোর করবে
                    
        asyncio.create_task(run_broadcast())
        return web.json_response({"success": True})
        
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)
