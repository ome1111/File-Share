# (©)Codexbotz
# Modified for Advanced Web Admin Panel

import os
import json
from aiohttp import web
from database.database import get_variable, set_variable, full_userbase

routes = web.RouteTableDef()

# আপনার ওয়েব প্যানেলের লগইন পাসওয়ার্ড (আপনি চাইলে এখান থেকে পরিবর্তন করতে পারবেন)
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
    return web.json_response({"status": "running", "message": "File Sharing Bot is Alive!"})

@routes.get("/admin")
async def admin_panel(request):
    """/admin লিংকে গেলে admin.html পেজটি শো করবে"""
    try:
        # মেইন ডিরেক্টরি থেকে admin.html ফাইলটি রিড করবে
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
    
    return web.json_response({
        "total_users": total_users,
        "token_1": token_1,
        "token_2": token_2,
        "upi_id": upi_id
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
            await set_variable(key, value)
            return web.json_response({"success": True, "message": f"{key} successfully updated!"})
        return web.json_response({"success": False, "error": "Invalid data format."}, status=400)
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)

