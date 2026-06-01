"""
Celery 异步任务配置。
生产环境安装 celery + redis 后取消注释 app.py 中的初始化代码。

安装: pip install celery redis
启动: celery -A celery_app.celery worker --loglevel=info
"""
import os

try:
    from celery import Celery
    celery = Celery('cloudnest', broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'))
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Shanghai',
        enable_utc=True,
        beat_schedule={
            'cleanup-trash-daily': {
                'task': 'tasks.cleanup.cleanup_deleted_files',
                'schedule': 86400.0,  # 每天执行一次
            },
        },
    )
except ImportError:
    celery = None
    print("[INFO] Celery not installed. Async tasks disabled. Install with: pip install celery redis")
