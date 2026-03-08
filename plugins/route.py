# (©) Modified for Advanced Web Admin Panel, IP Tracking & Earning System
import os
import asyncio
from datetime import datetime, timedelta
from aiohttp import web
from bson.objectid import ObjectId

from database.database import get_variable, set_variable, full_userbase, withdraw_data, user_data, database

# কালেকশনগুলো
shortlinks_db = database["shortlinks"]
ip_logs_db = database["ip_logs"] 

routes = web.RouteTableDef()
WEB_ADMIN_PASS = os.environ.get("WEB_ADMIN_PASS", "admin123")

def check_auth(request):
    auth_header = request.headers.get('Authorization')
    if auth_header == f"Bearer {WEB_ADMIN_PASS}":
        return True
    return False

@routes.get("/", allow_head=True)
async def root_route_handler(request):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="monetag" content="61d94185a23029ee0d3d5271037e5a35">
        
        <title>DriveLink ShareBot Server</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding-top: 50px; background-color: #f4f4f9; color: #333; }
            h1 { color: #4CAF50; }
        </style>
    </head>
    <body>
        <h1>✅ Server is Running Successfully!</h1>
        <p>DriveLink ShareBot & Monetization System is active.</p>
    </body>
    </html>
    """
    return web.Response(text=html_content, content_type="text/html")

# ==========================================
# 🚀 CUSTOM SHORTLINK VIEW PAGE WITH IP TRACKING
# ==========================================
@routes.get("/view/{link_id}")
async def custom_shortlink_view(request):
    link_id = request.match_info.get("link_id")
    
    # 🔥 FIX: await যোগ করা হয়েছে Async ডাটাবেসের জন্য
    link_data = await shortlinks_db.find_one({"_id": link_id})
    
    if not link_data or link_data.get("status") != "active":
        error_html = "<h2 style='text-align:center; color:#f38ba8; margin-top:20%; font-family:sans-serif;'>❌ Invalid or Expired Link!</h2>"
        return web.Response(text=error_html, content_type="text/html")
        
    client_ip = request.headers.get('X-Forwarded-For', request.remote)
    if client_ip:
        client_ip = client_ip.split(',')[0].strip()
        
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
    recent_visit = await ip_logs_db.find_one({
        "ip": client_ip,
        "link_id": link_id,
        "timestamp": {"$gte": twenty_four_hours_ago}
    })
    
    if not recent_visit:
        await shortlinks_db.update_one({"_id": link_id}, {"$inc": {"views": 1}})
        await ip_logs_db.insert_one({
            "ip": client_ip,
            "link_id": link_id,
            "timestamp": datetime.now()
        })
        
        # 🔥 MASTERSTROKE: ওয়েবসাইটের ভেতরেই টাকা অ্যাড করা!
        try:
            from database.database import add_view_to_user
            
            # ডাটাবেস থেকে সরাসরি user_id বের করা (যে লিংক বানিয়েছে)
            uploader_id = link_data.get("user_id")
            if uploader_id:
                await add_view_to_user(int(uploader_id)) # ইউজারের ব্যালেন্সে টাকা যোগ!
        except Exception as e:
            print("Web Reward Error:", e)
            
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
    
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{TITLE}}</title>
        {{AD_CODE_1}}
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f1015; color: #cdd6f4; margin: 0; padding: 0; display: flex; flex-direction: column; align-items: center; }
            .container { width: 90%; max-width: 800px; margin-top: 20px; background: #1e1e2e; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); text-align: center; }
            .file-title { font-size: 22px; font-weight: bold; color: #89b4fa; margin-bottom: 15px; word-break: break-word; }
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
        <div class="ad-box">{{AD_CODE_3}}</div>
        <div class="content-wrapper">
            <div class="container">
                <div class="file-title"><i class="fas fa-link"></i> {{TITLE}}</div>
                {{IMAGE_TAG}}
                <div class="ad-box">{{AD_CODE_2}}</div>
                <div id="timer-box" class="timer-box">
                    <i class="fas fa-spinner fa-spin"></i> Please wait <span id="countdown">{{TIMER}}</span> seconds...
                </div>
                <div class="ad-box">{{AD_CODE_4}}</div>
                <a href="{{DEST_URL}}" id="get-link-btn" class="get-link-btn"><i class="fas fa-external-link-alt"></i> Go To Link</a>
            </div>
        </div>
        <div class="sticky-footer-ad">{{AD_CODE_5}}</div>

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
    
    html_content = html_template.replace("{{TITLE}}", str(title)).replace("{{TIMER}}", str(timer)).replace("{{DEST_URL}}", str(destination_url)).replace("{{IMAGE_TAG}}", img_tag)
    html_content = html_content.replace("{{AD_CODE_1}}", ad_code_1 if ad_code_1 else "").replace("{{AD_CODE_2}}", ad_code_2 if ad_code_2 else "Body Ad Space").replace("{{AD_CODE_3}}", ad_code_3 if ad_code_3 else "Top Banner Ad Space").replace("{{AD_CODE_4}}", ad_code_4 if ad_code_4 else "Middle Banner Ad Space").replace("{{AD_CODE_5}}", ad_code_5 if ad_code_5 else '<div style="padding:10px; color:#6c7086;">Footer Sticky Ad Space</div>')
    
    return web.Response(text=html_content, content_type="text/html")

@routes.get("/admin")
async def admin_panel(request):
    try:
        with open("admin.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return web.Response(text=html_content, content_type="text/html")
    except FileNotFoundError:
        return web.Response(text="<h1>Error 404: admin.html not found!</h1>", status=404, content_type="text/html")

@routes.post("/api/login")
async def api_login(request):
    data = await request.json()
    if data.get("password", "") == WEB_ADMIN_PASS:
        return web.json_response({"success": True, "token": WEB_ADMIN_PASS})
    return web.json_response({"success": False, "error": "Invalid Password!"}, status=401)

@routes.get("/api/stats")
async def api_stats(request):
    if not check_auth(request): return web.json_response({"error": "Unauthorized"}, status=401)
    users = await full_userbase()
    return web.json_response({
        "total_users": len(users),
        "token_1": await get_variable("token_1", ""),
        "token_2": await get_variable("token_2", ""),
        "upi_id": await get_variable("upi_id", ""),
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
        key, value = data.get("key"), data.get("value")
        if key and value is not None:
            if key in ["cpm"]: value = float(value)
            elif key in ["del_timer", "timer_sec"]: value = int(value)
            await set_variable(key, value)
            return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)

@routes.get("/api/users")
async def api_get_users(request):
    if not check_auth(request): return web.json_response({"error": "Unauthorized"}, status=401)
    users = await user_data.find().sort("join_date", -1).limit(50).to_list(length=50)
    user_list = [{"id": u["_id"], "balance": round(u.get("balance", 0.0), 2), "views": u.get("views", 0), "banned": u.get("is_banned", False)} for u in users]
    return web.json_response({"success": True, "users": user_list})

@routes.get("/api/withdrawals")
async def api_get_withdrawals(request):
    if not check_auth(request): return web.json_response({"error": "Unauthorized"}, status=401)
    reqs = await withdraw_data.find({"status": "Pending"}).sort("date", -1).to_list(length=50)
    data = [{"id": str(r["_id"]), "user_id": r["user_id"], "amount": r["amount"], "method": r["method"], "details": r["details"], "date": r["date"].strftime("%d %b, %Y")} for r in reqs]
    return web.json_response({"success": True, "withdrawals": data, "requests": data}) # Added requests for compatibility

@routes.post("/api/withdrawals/approve")
@routes.post("/api/withdraw_action")
async def api_approve_withdrawal(request):
    if not check_auth(request): return web.json_response({"error": "Unauthorized"}, status=401)
    try:
        data = await request.json()
        req_id = data.get("id") or data.get("request_id")
        action = data.get("action", "Approved")
        
        await withdraw_data.update_one({"_id": ObjectId(req_id)}, {"$set": {"status": action}})
        if action == "Rejected":
            await user_data.update_one({"_id": int(data.get("user_id"))}, {"$inc": {"balance": float(data.get("amount", 0))}})
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)})

@routes.post("/api/users/ban")
async def api_ban_user(request):
    if not check_auth(request): return web.json_response({"error": "Unauthorized"}, status=401)
    try:
        data = await request.json()
        await user_data.update_one({"_id": int(data.get("user_id"))}, {"$set": {"is_banned": data.get("action") == "ban"}})
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)})

@routes.post("/api/user_action")
async def api_user_action(request):
    if not check_auth(request): return web.json_response({"error": "Unauthorized"}, status=401)
    try:
        data = await request.json()
        action, user_id, amount = data.get("action"), int(data.get("user_id", 0)), float(data.get("amount", 0.0))
        
        if action == "search":
            user = await user_data.find_one({"_id": user_id})
            if not user: return web.json_response({"success": False, "error": "User not found!"})
            return web.json_response({"success": True, "user": {"balance": round(user.get("balance", 0.0), 3), "views": user.get("views", 0), "is_banned": user.get("is_banned", False)}})
        
        elif action == "add": await user_data.update_one({"_id": user_id}, {"$inc": {"balance": amount}})
        elif action == "deduct": await user_data.update_one({"_id": user_id}, {"$inc": {"balance": -amount}})
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)})

@routes.post("/api/web_broadcast")
async def api_web_broadcast(request):
    if not check_auth(request): return web.json_response({"error": "Unauthorized"}, status=401)
    data = await request.json()
    if not data.get("text"): return web.json_response({"success": False, "error": "Empty message!"})
    
    async def run_broadcast():
        from bot import Bot 
        users = await full_userbase()
        for uid in users:
            try:
                await Bot.send_message(chat_id=uid, text=data.get("text"), disable_web_page_preview=True)
                await asyncio.sleep(0.5) 
            except Exception: pass 
            
    asyncio.create_task(run_broadcast())
    return web.json_response({"success": True})
