import pywhatkit as kit
from datetime import datetime, timedelta

# Current time + 10 seconds
send_time = datetime.now() + timedelta(seconds=10)

kit.sendwhatmsg(
    "+9779813609377",
    "Hello, this is a test message!",
    send_time.hour,
    send_time.minute
)