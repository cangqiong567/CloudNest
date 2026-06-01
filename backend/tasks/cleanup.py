"""
异步清理任务。
需要 Celery + Redis 环境。
"""
from datetime import datetime, timedelta


def register_cleanup_tasks(celery_app):
    """注册清理任务到 Celery"""

    if celery_app is None:
        return

    @celery_app.task(name='tasks.cleanup.cleanup_deleted_files')
    def cleanup_deleted_files():
        """清理回收站中超过 30 天的文件"""
        from app import create_app
        from extensions import db
        from models.file import File
        import os

        app = create_app()
        with app.app_context():
            threshold = datetime.utcnow() - timedelta(days=30)
            files = File.query.filter(
                File.is_deleted == True,
                File.deleted_at < threshold,
            ).all()

            count = 0
            for f in files:
                # 删除物理文件
                if f.storage_path and os.path.exists(f.storage_path):
                    try:
                        os.remove(f.storage_path)
                    except OSError:
                        pass
                db.session.delete(f)
                count += 1

            db.session.commit()
            return f'Cleaned up {count} files'

    @celery_app.task(name='tasks.cleanup.send_notification')
    def send_notification(user_id, title, body):
        """发送站内通知（可扩展为邮件/推送）"""
        # 预留接口，后续可对接邮件服务
        print(f"[Notification] User {user_id}: {title} - {body}")
        return True
