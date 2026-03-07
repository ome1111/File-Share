# (©)Codexbotz
# Modified for Advanced Web Admin Panel, IP Tracking & Earning System

import os
import json
import asyncio
from datetime import datetime, timedelta
from aiohttp import web
from bson.objectid import ObjectId

# Circular Import Error এড়ানোর জন্য bot ইম্পোর্ট করা হয়নি
from database.database import get_variable, set_variable, full_userbase, withdraw_data, user_data, database

# কালেকশনগুলো
shortlinks_db = database["shortlinks"]
ip_logs_db = database["ip_logs"] # 🔥 NEW: IP Tracking Database

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

# ==========================================
# 🚀 NEW: CUSTOM SHORTLINK VIEW PAGE WITH IP TRACKING
# ==========================================
@routes.get("/view/{link_id}")
async def custom_shortlink_view(request):
    """আপনার নিজস্ব শর্টলিংক পেজ"""
    link_id = request.match_info.get("link_id")
    
    # ডাটাবেস থেকে লিংক খোঁজা
    link_data = shortlinks_db.find_one({"_id": link_id})
    
    if not link_data or link_data.get("status") != "active":
        error_html = "<h2 style='text-align:center; color:#f38ba8; margin-top:20%; font-family:sans-serif;'>❌ Invalid or Expired Link!</h2>"
        return web.Response(text=error_html, content_type="text/html")
        
    # =======================================================
    # 🛡️ SECURE IP TRACKING SYSTEM
    # =======================================================
    # ইউজারের আসল IP বের করা (Cloudflare/Render Proxy পার হয়ে)
    client_ip = request.headers.get('X-Forwarded-For', request.remote)
    if client_ip:
        client_ip = client_ip.split(',')[0].strip()
        
    # চেক করবে গত ২৪ ঘণ্টায় এই IP থেকে ভিজিট হয়েছে কি না
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    recent_visit = ip_logs_db.find_one({
        "ip": client_ip,
        "link_id": link_id,
        "timestamp": {"$gte": twenty_four_hours_ago}
    })
    
    if not recent_visit:
        # নতুন ভিজিট হলে ভিউ কাউন্ট বাড়াবে এবং IP সেভ করবে
        shortlinks_db.update_one({"_id": link_id}, {"$inc": {"views": 1}})
        ip_logs_db.insert_one({
            "ip": client_ip,
            "link_id": link_id,
            "timestamp": datetime.now()
        })
    # যদি recent_visit থাকে, তবে ভিউ কাউন্ট বাড়বে না (Fake View Blocked!)
    # =======================================================
    
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
    
    token_1 = await get_variable("token_1", "")
    token_2 = await get_variable("token_2", "")
    upi_id = await get_variable("upi_id", "")
    cpm = await get_variable("cpm", 50.0)
    
    del_timer = await get_variable("del_timer", 0)
    start_msg = await get_variable("START_MSG", "")
    fsub_channels = await get_variable("fsub_channels", [])
    
    timer_sec = await get_variable("timer_sec", 10)
    ad_code_1 = await get_variable("ad_code_1", "")
    ad_code_2 = await get_variable("ad_code_2", "")
    ad_code_3 = await get_variable("ad_code_3", "")
    ad_code_4 = await get_variable("ad_code_4", "")
    ad_code_5 = await get_variable("ad_code_5", "")
    
    return web.json_response({
        "total_users": total_users,
        "token_1": token_1,
        "token_2": token_2,
        "upi_id": upi_id,
        "cpm": cpm,
        "del_timer": del_timer,
        "START_MSG": start_msg,
        "fsub_channels": fsub_channels,
        "timer_sec": timer_sec,
        "ad_code_1": ad_code_1,
        "ad_code_2": ad_code_2,
        "ad_code_3": ad_code_3,
        "ad_code_4": ad_code_4,
        "ad_code_5": ad_code_5
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
            elif key in ["del_timer", "timer_sec"]:
                value = int(value)
                
            await set_variable(key, value)
            return web.json_response({"success": True, "message": f"{key} successfully updated!"})
        return web.json_response({"success": False, "error": "Invalid data format."}, status=400)
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)

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

@routes.post("/api/user_action")
async def api_user_action(request):
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

@routes.post("/api/web_broadcast")
async def api_web_broadcast(request):
    if not check_auth(request):
        return web.json_response({"error": "Unauthorized"}, status=401)
        
    try:
        data = await request.json()
        text = data.get("text")
        
        if not text:
            return web.json_response({"success": False, "error": "Message is empty!"})
            
        async def run_broadcast():
            from bot import Bot 
            users = await full_userbase()
            for uid in users:
                try:
                    await Bot.send_message(chat_id=uid, text=text, disable_web_page_preview=True)
                    await asyncio.sleep(0.5) 
                except Exception:
                    pass 
                    
        asyncio.create_task(run_broadcast())
        return web.json_response({"success": True})
        
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)
