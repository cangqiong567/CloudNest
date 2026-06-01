import hashlib


def get_device_fingerprint(user_agent, ip):
    """根据 User-Agent 和 IP 生成设备指纹"""
    raw = f"{user_agent}|{ip}"
    return hashlib.md5(raw.encode('utf-8')).hexdigest()


def get_device_name(user_agent):
    """从 User-Agent 提取简易设备名"""
    ua = user_agent or ''
    ua_lower = ua.lower()

    # 浏览器
    if 'edg/' in ua_lower:
        browser = 'Edge'
    elif 'chrome' in ua_lower:
        browser = 'Chrome'
    elif 'firefox' in ua_lower:
        browser = 'Firefox'
    elif 'safari' in ua_lower:
        browser = 'Safari'
    else:
        browser = '未知浏览器'

    # 操作系统
    if 'windows' in ua_lower:
        os_name = 'Windows'
    elif 'macintosh' in ua_lower or 'mac os' in ua_lower:
        os_name = 'macOS'
    elif 'linux' in ua_lower:
        os_name = 'Linux'
    elif 'android' in ua_lower:
        os_name = 'Android'
    elif 'iphone' in ua_lower or 'ipad' in ua_lower:
        os_name = 'iOS'
    else:
        os_name = '未知系统'

    return f"{browser} / {os_name}"
