import os

# আপনার সার্ভারের (Render/Heroku) Environment Variables থেকে ডাটাবেসের লিংক নেবে
DB_URI = os.environ.get("DATABASE_URL", "")
JOIN_REQS_DB = DB_URI
DB_NAME = os.environ.get("DATABASE_NAME", "filesharexbot")
