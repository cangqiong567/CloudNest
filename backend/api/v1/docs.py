"""内置 API 文档页面，无需外部依赖"""
from flask import jsonify, render_template_string
from . import api_v1

API_DOCS = {
    'openapi': '3.0.0',
    'info': {
        'title': 'CloudNest API',
        'version': '1.0.0',
        'description': '个人云端工作台 API 文档',
    },
    'servers': [{'url': '/api/v1'}],
    'paths': {
        '/auth/register': {
            'post': {'summary': '用户注册', 'tags': ['认证'],
                     'requestBody': {'content': {'application/json': {'schema': {'type': 'object', 'properties': {'email': {'type': 'string'}, 'username': {'type': 'string'}, 'password': {'type': 'string'}}}}},
                     'responses': {'201': {'description': '注册成功'}, '400': {'description': '参数错误'}, '409': {'description': '已注册'}}}}
        },
        '/auth/login': {
            'post': {'summary': '用户登录', 'tags': ['认证'],
                     'requestBody': {'content': {'application/json': {'schema': {'type': 'object', 'properties': {'email': {'type': 'string'}, 'password': {'type': 'string'}}}}},
                     'responses': {'200': {'description': '登录成功'}, '401': {'description': '邮箱或密码错误'}}}}
        },
        '/auth/refresh': {
            'post': {'summary': '刷新令牌', 'tags': ['认证'], 'security': [{'bearerAuth': []}],
                     'responses': {'200': {'description': '刷新成功'}, '401': {'description': '令牌无效'}}}
        },
        '/auth/me': {
            'get': {'summary': '获取当前用户', 'tags': ['认证'], 'security': [{'bearerAuth': []}],
                    'responses': {'200': {'description': '成功'}}}
        },
        '/auth/2fa/setup': {
            'post': {'summary': '生成 2FA 密钥', 'tags': ['认证'], 'security': [{'bearerAuth': []}],
                     'responses': {'200': {'description': '返回密钥和 otpauth URI'}}}
        },
        '/auth/2fa/verify': {
            'post': {'summary': '验证并启用 2FA', 'tags': ['认证'], 'security': [{'bearerAuth': []}],
                     'responses': {'200': {'description': '2FA 已启用'}, '400': {'description': '验证码错误'}}}
        },
        '/files': {
            'get': {'summary': '文件列表', 'tags': ['文件'], 'security': [{'bearerAuth': []}],
                    'parameters': [{'name': 'parent_id', 'in': 'query', 'schema': {'type': 'integer'}}],
                    'responses': {'200': {'description': '成功'}}},
            'post': {'summary': '上传文件', 'tags': ['文件'], 'security': [{'bearerAuth': []}],
                     'responses': {'201': {'description': '上传成功'}}}
        },
        '/files/folder': {
            'post': {'summary': '新建文件夹', 'tags': ['文件'], 'security': [{'bearerAuth': []}],
                     'responses': {'201': {'description': '创建成功'}}}
        },
        '/files/{id}/download': {
            'get': {'summary': '下载文件', 'tags': ['文件'], 'security': [{'bearerAuth': []}],
                    'responses': {'200': {'description': '文件内容'}}}
        },
        '/files/{id}/share': {
            'post': {'summary': '创建分享链接', 'tags': ['文件'], 'security': [{'bearerAuth': []}],
                     'responses': {'201': {'description': '分享链接'}}}
        },
        '/share/{code}': {
            'get': {'summary': '访问分享', 'tags': ['文件'],
                    'responses': {'200': {'description': '文件信息'}, '404': {'description': '链接无效'}}}
        },
        '/notes': {
            'get': {'summary': '笔记列表', 'tags': ['笔记'], 'security': [{'bearerAuth': []}],
                    'parameters': [{'name': 'search', 'in': 'query', 'schema': {'type': 'string'}}],
                    'responses': {'200': {'description': '成功'}}},
            'post': {'summary': '创建笔记', 'tags': ['笔记'], 'security': [{'bearerAuth': []}],
                     'responses': {'201': {'description': '创建成功'}}}
        },
        '/notes/{id}/versions': {
            'get': {'summary': '版本历史', 'tags': ['笔记'], 'security': [{'bearerAuth': []}],
                    'responses': {'200': {'description': '成功'}}}
        },
        '/notes/{id}/export/{format}': {
            'get': {'summary': '导出笔记', 'tags': ['笔记'], 'security': [{'bearerAuth': []}],
                    'responses': {'200': {'description': '导出内容'}}}
        },
        '/tasks': {
            'get': {'summary': '任务列表', 'tags': ['任务'], 'security': [{'bearerAuth': []}],
                    'responses': {'200': {'description': '成功'}}},
            'post': {'summary': '创建任务', 'tags': ['任务'], 'security': [{'bearerAuth': []}],
                     'responses': {'201': {'description': '创建成功'}}}
        },
        '/tasks/stats': {
            'get': {'summary': '任务统计', 'tags': ['任务'], 'security': [{'bearerAuth': []}],
                    'responses': {'200': {'description': '成功'}}}
        },
        '/task-columns': {
            'get': {'summary': '看板列列表', 'tags': ['任务'], 'security': [{'bearerAuth': []}],
                    'responses': {'200': {'description': '成功'}}},
            'post': {'summary': '创建看板列', 'tags': ['任务'], 'security': [{'bearerAuth': []}],
                     'responses': {'201': {'description': '创建成功'}}}
        },
        '/settings/export': {
            'get': {'summary': '导出所有数据', 'tags': ['设置'], 'security': [{'bearerAuth': []}],
                    'responses': {'200': {'description': 'JSON 数据包'}}}
        },
    },
    'components': {
        'securitySchemes': {
            'bearerAuth': {'type': 'http', 'scheme': 'bearer', 'bearerFormat': 'JWT'}
        }
    },
    'tags': [
        {'name': '认证', 'description': '注册/登录/2FA'},
        {'name': '文件', 'description': '文件管理/分享'},
        {'name': '笔记', 'description': '笔记/笔记本/标签'},
        {'name': '任务', 'description': '任务/看板列'},
        {'name': '设置', 'description': '用户设置/数据导出'},
    ],
}


@api_v1.route('/docs', methods=['GET'])
def api_docs():
    """返回 OpenAPI JSON"""
    return jsonify(API_DOCS)


@api_v1.route('/docs/ui', methods=['GET'])
def api_docs_ui():
    """Swagger UI 页面"""
    return render_template_string(SWAGGER_UI_HTML)


SWAGGER_UI_HTML = '''<!DOCTYPE html>
<html>
<head>
  <title>CloudNest API Docs</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({ url: '/api/v1/docs', dom_id: '#swagger-ui' })
  </script>
</body>
</html>'''
