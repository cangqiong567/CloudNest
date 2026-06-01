import pytest
from app import create_app
from extensions import db


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """注册并返回带 JWT 的请求头"""
    resp = client.post('/api/v1/auth/register', json={
        'email': 'test@example.com',
        'username': 'testuser',
        'password': '123456',
    })
    token = resp.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}
