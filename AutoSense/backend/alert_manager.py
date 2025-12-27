import time

_last_alert_time = 0
_last_state = 0
COOLDOWN = 30  # seconds

def should_alert(current_state):
    global _last_alert_time, _last_state
    now = time.time()

    if current_state != _last_state and (now - _last_alert_time) > COOLDOWN:
        _last_alert_time = now
        _last_state = current_state
        return True

    _last_state = current_state
    return False
