# (©)Codexbotz
# Modified for Advanced Web Admin Panel & Custom Shortlink System

import os
import json
import asyncio
from aiohttp import web
from bson.objectid import ObjectId

# Database imports
from database.database import get_variable, set_variable, full_userbase, withdraw_data, user_data, database

# নতুন কালেকশন: শর্টলিংকের ডাটা সেভ রাখার জন্য
shortlinks_db = database["shortlinks"]

routes = web.RouteTableDef()

# আপনার ওয়েব প্যানেলের লগইন পাসওয়ার্ড
WEB_ADMIN_PASS = os.environ.get("WEB_ADMIN_PASS", "admin123")

def check_auth(request):
    auth_header = request.headers.get('Authorization')
    if auth_header == f"Bearer {WEB_ADMIN_PASS}":
        return True
    return False

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    return web.json_response({"status": "running", "message": "File Sharing & Earning Bot is Alive!"})

# ==========================================
# 🚀 NEW: CUSTOM SHORTLINK VIEW PAGE (PHP TO PYTHON)
# ==========================================
@routes.get("/view/{link_id}")
async def custom_shortlink_view(request):
    """আপনার নিজস্ব শর্টলিংক পেজ (PHP ফাইলের পাইথন ভার্সন)"""
    link_id = request.match_info.get("link_id")
    
    # ডাটাবেস থেকে লিংক খোঁজা
    link_data = shortlinks_db.find_one({"_id": link_id})
    
    if not link_data or link_data.get("status") != "active":
        error_html = "<h2 style='text-align:center; color:#f38ba8; margin-top:20%; font-family:sans-serif;'>❌ Invalid or Expired Link!</h2>"
        return web.Response(text=error_html, content_type="text/html")
        
    # ভিউ (Views) কাউন্ট আপডেট করা (+1)
    shortlinks_db.update_one({"_id": link_id}, {"$inc": {"views": 1}})
    
    # ডাটাবেস থেকে সেটিংস এবং অ্যাড কোড বের করা
    timer = await get_variable("timer_sec", 10)
    ad_code_1 = await get_variable("ad_code_1", "")
    ad_code_2 = await get_variable("ad_code_2", "")
    ad_code_3 = await get_variable("ad_code_3", "")
    ad_code_4 = await get_variable("ad_code_4", "")
    ad_code_5 = await get_variable("ad_code_5", "")
    
    title = link_data.get("title", "Download File")
    destination_url = link_data.get("destination_url", "#")
    image_url = link_data.get("image_url", "")
    
    img_tag = f'<img src="{image_url}" class="file-image" alt="Thumbnail">' if image_url else ""
    
    # আপনার দেওয়া হুবহু HTML ও CSS ডিজাইন
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{TITLE}} - Download</title>
        
        {{AD_CODE_1}}
        
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f1015; color: #cdd6f4; margin: 0; padding: 0; display: flex; flex-direction: column; align-items: center; }
            .container { width: 90%; max-width: 800px; margin-top: 20px; background: #1e1e2e; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); text-align: center; }
            .file-title { font-size: 22px; font-weight: bold; color: #89b4fa; margin-bottom: 15px; }
            .file-image { max-width: 100%; height: auto; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.5); }
            .ad-box { width: 100%; min-height: 50px; background: #11111b; border: 1px dashed #45475a; margin: 15px 0; display: flex; align-items: center; justify-content: center; color: #6c7086; overflow: hidden; }
            .timer-box { font-size: 20px; font-weight: bold; color: #f9e2af; background: #313244; padding: 15px; border-radius: 8px; margin: 20px 0; }
            .get-link-btn { display: none; background: #a6e3a1; color: #1e1e2e; text-decoration: none; padding: 15px 30px; font-size: 18px; font-weight: bold; border-radius: 8px; margin: 20px auto; transition: 0.3s; box-shadow: 0 4px 10px rgba(166, 227, 161, 0.4); }
            .get-link-btn:hover { background: #94e2d5; }
            .sticky-footer-ad { position: fixed; bottom: 0; width: 100%; background: #181825; text-align: center; z-index: 999; border-top: 1px solid #313244; }
            .content-wrapper { padding-bottom: 80px; width: 100%; display: flex; flex-direction: column; align-items: center; }
        </style>
    </head>
    <body>

        <div class="ad-box">
            {{AD_CODE_3}}
        </div>

        <div class="content-wrapper">
            <div class="container">
                <div class="file-title"><i class="fas fa-file-alt"></i> {{TITLE}}</div>
                
                {{IMAGE_TAG}}

                <div class="ad-box">
                    {{AD_CODE_2}}
                </div>

                <div id="timer-box" class="timer-box">
                    <i class="fas fa-spinner fa-spin"></i> Please wait <span id="countdown">{{TIMER}}</span> seconds...
                </div>

                <div class="ad-box">
                    {{AD_CODE_4}}
                </div>

                <a href="{{DEST_URL}}" id="get-link-btn" class="get-link-btn">
                    <i class="fas fa-download"></i> Get Link
                </a>
                
            </div>
        </div>

        <div class="sticky-footer-ad">
            {{AD_CODE_5}}
        </div>

        <script>
            var timeLeft = {{TIMER}};
            var countdownEl = document.getElementById('countdown');
            var timerBox = document.getElementById('timer-box');
            var getLinkBtn = document.getElementById('get-link-btn');

            var timerInterval = setInterval(function() {
                timeLeft--;
                countdownEl.innerText = timeLeft;

                if (timeLeft <= 0) {
                    clearInterval(timerInterval);
                    timerBox.style.display = 'none';
                    getLinkBtn.style.display = 'inline-block';
                }
            }, 1000);
        </script>

    </body>
    </html>
    """
    
    # ডায়নামিক ভ্যালুগুলো HTML এ বসানো
    html_content = html_template.replace("{{TITLE}}", str(title))
    html_content = html_content.replace("{{TIMER}}", str(timer))
    html_content = html_content.replace("{{DEST_URL}}", str(destination_url))
    html_content = html_content.replace("{{IMAGE_TAG}}", img_tag)
    
    html_content = html_content.replace("{{AD_CODE_1}}", ad_code_1 if ad_code_1 else "")
    html_content = html_content.replace("{{AD_CODE_2}}", ad_code_2 if ad_code_2 else "Body Ad Space")
    html_content = html_content.replace("{{AD_CODE_3}}", ad_code_3 if ad_code_3 else "Top Banner Ad Space")
    html_content = html_content.replace("{{AD_CODE_4}}", ad_code_4 if ad_code_4 else "Middle Banner Ad Space")
    html_content = html_content.replace("{{AD_CODE_5}}", ad_code_5 if ad_code_5 else '<div style="padding:10px; color:#6c7086;">Footer Sticky Ad Space</div>')
    
    return web.Response(text=html_content, content_type="text/html")

# ==========================================
# ⚙️ ADMIN APIs (Stats, Login, Update)
# ==========================================

@routes.get("/admin")
async def admin_panel(request):
    try:
        with open("admin.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return web.Response(text=html_content, content_type="text/html")
    except FileNotFoundError:
        return web.Response(text="<h1>Error 404: admin.html file not found!</h1>", status=404, content_type="text/html")

@routes.post("/api/login")
async def api_login(request):
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
    if not check_auth(request): return web.json_response({"error": "Unauthorized"}, status=401)
    
    users = await full_userbase()
    
    return web.json_response({
        "total_users": len(users),
        "cpm": await get_variable("cpm", 50.0),
        "del_timer": await get_variable("del_timer", 0),
        "START_MSG": await get_variable("START_MSG", ""),
        "fsub_channels": await get_variable("fsub_channels", []),
        "timer_sec": await get_variable("timer_sec", 10),
        "ad_code_1": await get_variable("ad_code_1", ""),
        "ad_code_2": await get_variable("ad_code_2", ""),
        "ad_code_3": await get_variable("ad_code_3", ""),
        "ad_code_4": await get_variable("ad_code_4", ""),
        "ad_code_5": await get_variable("ad_code_5", "")
    })

@routes.post("/api/update")
async def api_update(request):
    if not check_auth(request): return web.json_response({"error": "Unauthorized"}, status=401)
    try:
        data = await request.json()
        key = data.get("key")
        value = data.get("value")
        
        if key:
            if key in ["cpm"]: value = float(value)
            elif key in ["del_timer", "timer_sec"]: value = int(value)
            await set_variable(key, value)
            return web.json_response({"success": True})
        return web.json_response({"success": False, "error": "Invalid data format."}, status=400)
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)

# ==========================================
# 💸 WITHDRAWAL & USER APIs
# ==========================================

@routes.get("/api/withdrawals")
async def api_get_withdrawals(request):
    if not check_auth(request): return web.json_response({"error": "Unauthorized"}, status=401)
    try:
        cursor = withdraw_data.find({"status": "Pending"}).sort("date", -1)
        requests = [{"_id": str(r["_id"]), "user_id": r["user_id"], "amount": r["amount"], "method": r["method"], "details": r["details"], "date": r["date"].strftime("%d %b, %Y")} for r in cursor]
        return web.json_response({"success": True, "requests": requests})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)

@routes.post("/api/withdraw_action")
async def api_withdraw_action(request):
    if not check_auth(request): return web.json_response({"error": "Unauthorized"}, status=401)
    try:
        data = await request.json()
        req_id, action, user_id, amount = data.get("request_id"), data.get("action"), data.get("user_id"), float(data.get("amount", 0))
        withdraw_data.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": action}})
        if action == "Rejected": user_data.update_one({"_id": int(user_id)}, {"$inc": {"balance": amount}})
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)

@routes.post("/api/user_action")
async def api_user_action(request):
    if not check_auth(request): return web.json_response({"error": "Unauthorized"}, status=401)
    try:
        data = await request.json()
        action, user_id, amount = data.get("action"), int(data.get("user_id", 0)), float(data.get("amount", 0.0))
        if not user_id: return web.json_response({"success": False, "error": "Invalid User ID"})
        user = user_data.find_one({"_id": user_id})
        
        if action == "search":
            if not user: return web.json_response({"success": False, "error": "User not found!"})
            return web.json_response({"success": True, "user": {"balance": round(user.get("balance", 0.0), 3), "views": user.get("views", 0), "is_banned": user.get("is_banned", False)}})
        elif action == "add": user_data.update_one({"_id": user_id}, {"$inc": {"balance": amount}})
        elif action == "deduct": user_data.update_one({"_id": user_id}, {"$inc": {"balance": -amount}})
        elif action == "ban": user_data.update_one({"_id": user_id}, {"$set": {"is_banned": True}})
        elif action == "unban": user_data.update_one({"_id": user_id}, {"$set": {"is_banned": False, "warnings": 0}})
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)

@routes.post("/api/web_broadcast")
async def api_web_broadcast(request):
    if not check_auth(request): return web.json_response({"error": "Unauthorized"}, status=401)
    try:
        data = await request.json()
        text = data.get("text")
        if not text: return web.json_response({"success": False, "error": "Message is empty!"})
        
        async def run_broadcast():
            from bot import Bot 
            users = await full_userbase()
            for uid in users:
                try:
                    await Bot.send_message(chat_id=uid, text=text, disable_web_page_preview=True)
                    await asyncio.sleep(0.5)
                except Exception: pass
                    
        asyncio.create_task(run_broadcast())
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)
