import psutil, sqlite3, time
from database import init_db

init_db()

def get_stats():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent
    }

def log_stats():
    while True:
        stats = get_stats()

        conn = sqlite3.connect("autosense.db")
        c = conn.cursor()

        c.execute(
            "INSERT INTO system_stats (cpu, ram, disk) VALUES (?,?,?)",
            (stats["cpu"], stats["ram"], stats["disk"])
        )

        conn.commit()
        conn.close()
        time.sleep(1)
