"""
轻量级 TOTP 实现（RFC 6238），无需 pyotp 依赖。
使用标准库 hmac + hashlib + struct。
"""
import hmac
import hashlib
import struct
import time
import secrets
import base64


def generate_secret(length=20):
    """生成随机 Base32 密钥"""
    raw = secrets.token_bytes(length)
    return base64.b32encode(raw).decode('utf-8').rstrip('=')


def _base32_decode(s):
    """手动 Base32 解码"""
    s = s.upper().rstrip('=')
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
    bits = ''
    for c in s:
        val = alphabet.find(c)
        if val < 0:
            continue
        bits += format(val, '05b')
    result = bytearray()
    for i in range(0, len(bits) - 7, 8):
        result.append(int(bits[i:i+8], 2))
    return bytes(result)


def _int_to_bytes(n):
    return struct.pack('>Q', n)


def generate_totp(secret, time_step=30, digits=6):
    """生成当前时间的 TOTP 验证码"""
    counter = int(time.time()) // time_step
    key = _base32_decode(secret)
    counter_bytes = _int_to_bytes(counter)
    hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
    offset = hmac_hash[-1] & 0x0F
    truncated = struct.unpack('>I', hmac_hash[offset:offset+4])[0] & 0x7FFFFFFF
    code = truncated % (10 ** digits)
    return str(code).zfill(digits)


def verify_totp(secret, code, time_step=30, digits=6, window=1):
    """验证 TOTP 验证码，允许前后各 window 个时间窗口的偏差"""
    counter = int(time.time()) // time_step
    key = _base32_decode(secret)
    for offset in range(-window, window + 1):
        counter_bytes = _int_to_bytes(counter + offset)
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        trunc_offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack('>I', hmac_hash[trunc_offset:trunc_offset+4])[0] & 0x7FFFFFFF
        expected = str(truncated % (10 ** digits)).zfill(digits)
        if hmac.compare_digest(expected, code):
            return True
    return False


def get_otpauth_uri(secret, email, issuer='CloudNest'):
    """生成 OTP Auth URI（用于生成二维码）"""
    return f'otpauth://totp/{issuer}:{email}?secret={secret}&issuer={issuer}&digits=6'
