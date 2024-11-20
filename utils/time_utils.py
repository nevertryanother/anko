from datetime import datetime
import pytz

def format_voice_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60

    if hours > 0:
        return f"{hours:.0f}ч {minutes:.0f}м"
    
    else:
        return f"{minutes:.0f}м"
    
def get_moscow_time():
    return datetime.now(pytz.timezone('Europe/Moscow'))