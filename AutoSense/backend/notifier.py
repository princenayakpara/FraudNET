from win10toast import ToastNotifier

toaster = ToastNotifier()

def send_alert(title, message):
    toaster.show_toast(
        title,
        message,
        duration=4,
        threaded=True
    )
