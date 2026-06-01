from flask import jsonify


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({'error': '请求参数错误', 'message': str(e)}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({'error': '未授权', 'message': str(e)}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({'error': '禁止访问', 'message': str(e)}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': '资源不存在', 'message': str(e)}), 404

    @app.errorhandler(409)
    def conflict(e):
        return jsonify({'error': '资源冲突', 'message': str(e)}), 409

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': '服务器内部错误', 'message': '请稍后重试'}), 500
