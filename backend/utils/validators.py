import re


def validate_email(email):
    if not email or not isinstance(email, str):
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_password(password):
    if not password or not isinstance(password, str):
        return False, '密码不能为空'
    if len(password) < 6:
        return False, '密码长度至少6位'
    if len(password) > 128:
        return False, '密码长度不能超过128位'
    return True, ''


def validate_username(username):
    if not username or not isinstance(username, str):
        return False, '用户名不能为空'
    username = username.strip()
    if len(username) < 2:
        return False, '用户名长度至少2位'
    if len(username) > 50:
        return False, '用户名长度不能超过50位'
    if not re.match(r'^[a-zA-Z0-9_一-鿿]+$', username):
        return False, '用户名只能包含字母、数字、下划线和中文'
    return True, ''
