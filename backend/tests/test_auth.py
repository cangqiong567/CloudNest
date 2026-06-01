def test_register(client):
    resp = client.post('/api/v1/auth/register', json={
        'email': 'new@example.com',
        'username': 'newuser',
        'password': '123456',
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['user']['email'] == 'new@example.com'
    assert 'access_token' in data
    assert 'refresh_token' in data


def test_register_duplicate_email(client):
    client.post('/api/v1/auth/register', json={
        'email': 'dup@example.com', 'username': 'user1', 'password': '123456',
    })
    resp = client.post('/api/v1/auth/register', json={
        'email': 'dup@example.com', 'username': 'user2', 'password': '123456',
    })
    assert resp.status_code == 409


def test_register_invalid_email(client):
    resp = client.post('/api/v1/auth/register', json={
        'email': 'bad', 'username': 'user', 'password': '123456',
    })
    assert resp.status_code == 400


def test_register_short_password(client):
    resp = client.post('/api/v1/auth/register', json={
        'email': 'a@b.com', 'username': 'user', 'password': '123',
    })
    assert resp.status_code == 400


def test_login_success(client):
    client.post('/api/v1/auth/register', json={
        'email': 'login@example.com', 'username': 'loginuser', 'password': '123456',
    })
    resp = client.post('/api/v1/auth/login', json={
        'email': 'login@example.com', 'password': '123456',
    })
    assert resp.status_code == 200
    assert 'access_token' in resp.get_json()


def test_login_wrong_password(client):
    client.post('/api/v1/auth/register', json={
        'email': 'a@b.com', 'username': 'user', 'password': '123456',
    })
    resp = client.post('/api/v1/auth/login', json={
        'email': 'a@b.com', 'password': 'wrong',
    })
    assert resp.status_code == 401


def test_get_me(client, auth_headers):
    resp = client.get('/api/v1/auth/me', headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()['user']['email'] == 'test@example.com'


def test_get_me_unauthorized(client):
    resp = client.get('/api/v1/auth/me')
    assert resp.status_code in (401, 422)


def test_refresh_token(client):
    reg = client.post('/api/v1/auth/register', json={
        'email': 'r@b.com', 'username': 'refuser', 'password': '123456',
    })
    refresh = reg.get_json()['refresh_token']
    resp = client.post('/api/v1/auth/refresh', headers={'Authorization': f'Bearer {refresh}'})
    assert resp.status_code == 200
    assert 'access_token' in resp.get_json()
