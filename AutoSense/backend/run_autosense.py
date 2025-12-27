import os
import sys
import subprocess

BASE = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)

subprocess.Popen([
    sys.executable,
    "-m", "uvicorn",
    "main:app",
    "--host", "127.0.0.1",
    "--port", "8000"
])

os.system("start http://127.0.0.1:8000")
