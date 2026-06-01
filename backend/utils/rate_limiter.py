"""轻量级内存限流器，无需 Redis/外部依赖"""
import time
from functools import wraps
from collections import defaultdict
from flask import request, jsonify, current_app

# 存储结构: {key: [timestamp1, timestamp2, ...]}
_hits = defaultdict(list)


def rate_limit(max_requests: int, window_seconds: int, key_func=None):
    """
    装饰器：限制某接口在时间窗口内的请求次数。

    Args:
        max_requests: 窗口内最大请求数
        window_seconds: 时间窗口（秒）
        key_func: 自定义限流键函数，默认按 IP
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 测试环境可跳过限流
            if not current_app.config.get('RATE_LIMIT_ENABLED', True):
                return f(*args, **kwargs)
            if key_func:
                key = key_func()
            else:
                key = request.remote_addr or 'unknown'
            full_key = f"{f.__name__}:{key}"

            now = time.time()
            # 清理过期记录
            _hits[full_key] = [t for t in _hits[full_key] if now - t < window_seconds]

            if len(_hits[full_key]) >= max_requests:
                retry_after = int(window_seconds - (now - _hits[full_key][0]))
                return jsonify({
                    'error': 'Too many requests',
                    'retry_after': max(retry_after, 1),
                }), 429

            _hits[full_key].append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator
