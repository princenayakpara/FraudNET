import sqlite3, psutil

def add_blacklist(app_name):
    conn = sqlite3.connect("autosense.db")
    c = conn.cursor()

    c.execute("""
      CREATE TABLE IF NOT EXISTS blacklist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
      )
    """)

    c.execute("INSERT OR IGNORE INTO blacklist(name) VALUES(?)", (app_name,))
    conn.commit()
    conn.close()

def get_blacklist():
    conn = sqlite3.connect("autosense.db")
    c = conn.cursor()
    c.execute("SELECT name FROM blacklist")
    apps = [i[0] for i in c.fetchall()]
    conn.close()
    return {"apps": apps}

def kill_blacklisted():
    bl = get_blacklist()["apps"]

    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] in bl:
                proc.kill()
        except:
            pass
