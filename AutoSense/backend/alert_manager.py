import winsound
import datetime

def send_alert(status, cpu, ram, disk):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")

    print("\n🚨 AUTO SENSE ALERT 🚨")
    print(f"Time   : {timestamp}")
    print(f"Status : {status}")
    print(f"CPU    : {cpu}%")
    print(f"RAM    : {ram}%")
    print(f"Disk   : {disk}%")
    print("⚠ Please check your system!\n")

    # Beep alert
    winsound.Beep(1200, 700)
