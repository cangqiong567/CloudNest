import os
from flask import Flask, send_from_directory
from config import config_map
from extensions import db, jwt, cors, migrate


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # 上传文件目录
    upload_dir = os.path.join(app.root_path, 'uploads')
    os.makedirs(os.path.join(upload_dir, 'avatars'), exist_ok=True)

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    migrate.init_app(app, db)

    # 注册蓝图
    from api.v1 import api_v1
    app.register_blueprint(api_v1, url_prefix='/api/v1')

    # 全局错误处理
    from middleware.error_handler import register_error_handlers
    register_error_handlers(app)

    # 静态文件服务（头像等上传文件）
    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(upload_dir, filename)

    # 创建数据库表
    with app.app_context():
        from models import User, LoginRecord, TrustedDevice, File, FileShare, Note, Notebook, Tag, NoteVersion, Task, TaskColumn  # noqa: F401
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
