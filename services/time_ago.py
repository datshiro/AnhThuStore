# -*- coding: utf-8 -*-
def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time, datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "Vừa xong"
        if second_diff < 60:
            return str(second_diff) + " giây trước"
        if second_diff < 120:
            return "Một phút trước"
        if second_diff < 3600:
            return str(second_diff / 60) + " phút trước"
        if second_diff < 7200:
            return "Một tiếng trước"
        if second_diff < 86400:
            return str(second_diff / 3600) + " giờ trước"
    if day_diff == 1:
        return "Hôm qua"
    if day_diff < 7:
        return str(day_diff) + " ngày trước"
    if day_diff < 31:
        return str(day_diff / 7) + " tuần trước"
    if day_diff < 365:
        return str(day_diff / 30) + " tháng trước"
    return str(day_diff / 365) + " năm trước"
