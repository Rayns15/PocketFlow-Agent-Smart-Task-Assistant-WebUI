from datetime import datetime

def get_current_timestamp():
    """Provides ISO-standard timestamps for the agent's logs."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")