"""
notification_manager.py — prevents duplicate SMS
Add this to services/notifications/ if not already present
"""

# In-memory dedup store — resets on server restart
_sent_notifications = {}  # { key: timestamp }

def should_send(key: str, cooldown_minutes: int = 60) -> bool:
    """
    Returns True if we should send this notification.
    Prevents duplicate sends within cooldown_minutes.
    """
    from datetime import datetime, timedelta
    now = datetime.now()
    if key in _sent_notifications:
        last_sent = _sent_notifications[key]
        if now - last_sent < timedelta(minutes=cooldown_minutes):
            return False
    _sent_notifications[key] = now
    return True

def mark_sent(key: str):
    from datetime import datetime
    _sent_notifications[key] = datetime.now()