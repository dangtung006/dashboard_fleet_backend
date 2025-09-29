import time
from datetime import datetime


def is_elapsed(start_time, minutes: int) -> bool:
    """
    Kiểm tra xem từ start_time đến hiện tại đã đủ 'minutes' phút chưa.
    - start_time có thể là datetime hoặc timestamp (float/int).
    """
    if isinstance(start_time, datetime):
        start_ts = start_time.timestamp()
    elif isinstance(start_time, (int, float)):
        start_ts = float(start_time)
    else:
        raise ValueError("start_time phải là datetime hoặc timestamp")

    now_ts = time.time()
    return (now_ts - start_ts) >= minutes * 60
