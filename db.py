import sqlite3, json
class DB:
    def __init__(self, path="tele_analytics.db"):
        self.path = path
        self._init_db()
    def _init_db(self):
        with sqlite3.connect(self.path) as conn:
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                plan TEXT DEFAULT 'freemium',
                limit INTEGER DEFAULT 1000,
                chats INTEGER DEFAULT 1,
                extras TEXT DEFAULT '{}'
            )""")
            c.execute("""CREATE TABLE IF NOT EXISTS messages_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                sender TEXT,
                text TEXT
            )""")
            conn.commit()
    def ensure_user(self, user_id):
        with sqlite3.connect(self.path) as conn:
            c = conn.cursor()
            c.execute("SELECT 1 FROM users WHERE user_id=?", (user_id,))
            if not c.fetchone():
                c.execute("INSERT INTO users(user_id) VALUES(?)", (user_id,))
            conn.commit()
    def get_user(self, user_id):
        with sqlite3.connect(self.path) as conn:
            c = conn.cursor()
            c.execute("SELECT plan,limit,chats,extras FROM users WHERE user_id=?", (user_id,))
            row = c.fetchone()
            if not row:
                return {"plan":"freemium","limit":1000,"chats":1,"extras":{}}
            plan,limit,chats,extras = row
            return {"plan":plan,"limit":limit,"chats":chats,"extras": json.loads(extras)}
    def set_plan(self, user_id, plan):
        mapping = {
            "freemium": (1000,1),
            "basic": (5000,2),
            "pro": (25000,10)
        }
        limit,chats = mapping.get(plan, (1000,1))
        with sqlite3.connect(self.path) as conn:
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO users(user_id, plan, limit, chats, extras) VALUES(?,?,?,?,?)",
                      (user_id, plan, limit, chats, json.dumps({})))
            conn.commit()
    def search_messages(self, user_id, keyword, since=None, from_user=None):
        q = "SELECT date,sender,text FROM messages_cache WHERE text LIKE ?"
        params = [f"%{keyword}%"]
        if since:
            q += " AND date >= ?"
            params.append(since)
        if from_user:
            q += " AND sender = ?"
            params.append(from_user.lstrip("@"))
        q += " ORDER BY date DESC LIMIT 200"
        with sqlite3.connect(self.path) as conn:
            c = conn.cursor()
            c.execute(q, params)
            rows = c.fetchall()
            return [{"date":r[0],"sender":r[1],"text":r[2]} for r in rows]
    def cache_messages(self, user_id, messages):
        with sqlite3.connect(self.path) as conn:
            c = conn.cursor()
            for m in messages:
                c.execute("INSERT INTO messages_cache(user_id,date,sender,text) VALUES(?,?,?,?)",
                          (user_id, m.get("date"), m.get("sender"), m.get("text")))
            conn.commit()

