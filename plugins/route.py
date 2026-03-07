# (©)Codexbotz
# Modified for Advanced Web Admin Panel & Earning System

import os
import json
from aiohttp import web
from bson.objectid import ObjectId
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
    
    # ডাটাবেস থেকে ইউজার সংখ্যা বের করা
    users = await full_userbase()
    total_users = len(users)
    
    # ডাটাবেস থেকে সেটিং ভ্যালুগুলো বের করা
    token_1 = await get_variable("token_1", "")
    token_2 = await get_variable("token_2", "")
    upi_id = await get_variable("upi_id", "")
    cpm = await get_variable("cpm", 50.0) # CPM রেট
    
    return web.json_response({
        "total_users": total_users,
        "token_1": token_1,
        "token_2": token_2,
        "upi_id": upi_id,
        "cpm": cpm
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
            # CPM হলে Float এ কনভার্ট করে সেভ করবে
            if key == "cpm":
                value = float(value)
            await set_variable(key, value)
            return web.json_response({"success": True, "message": f"{key} successfully updated!"})
        return web.json_response({"success": False, "error": "Invalid data format."}, status=400)
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)

# ==========================================
# 💸 NEW: WITHDRAWAL REQUEST APIs
# ==========================================

@routes.get("/api/withdrawals")
async def api_get_withdrawals(request):
    """ওয়েব প্যানেলে Pending উইথড্র লিস্ট দেখাবে"""
    if not check_auth(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        # ডাটাবেস থেকে শুধু Pending রিকোয়েস্টগুলো বের করবে
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
    """Paid বা Reject বাটনে ক্লিক করলে ডাটাবেস আপডেট করবে"""
    if not check_auth(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        data = await request.json()
        req_id = data.get("request_id")
        action = data.get("action") # "Paid" or "Rejected"
        user_id = data.get("user_id")
        amount = float(data.get("amount", 0))
        
        # ১. রিকোয়েস্টের স্ট্যাটাস আপডেট করা
        withdraw_data.update_one(
            {"_id": ObjectId(req_id)}, 
            {"$set": {"status": action}}
        )
        
        # ২. যদি অ্যাডমিন রিকোয়েস্ট "Reject" করে, তবে ইউজারের টাকা ব্যাক (Refund) করে দেওয়া
        if action == "Rejected":
            user_data.update_one(
                {"_id": int(user_id)}, 
                {"$inc": {"balance": amount}}
            )
            
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)

