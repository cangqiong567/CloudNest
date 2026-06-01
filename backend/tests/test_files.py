import io


def test_create_folder(client, auth_headers):
    resp = client.post('/api/v1/files/folder', json={'name': 'Docs'}, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()['file']['is_folder'] is True


def test_upload_file(client, auth_headers):
    data = {'file': (io.BytesIO(b'hello world'), 'test.txt')}
    resp = client.post('/api/v1/files', data=data, headers=auth_headers, content_type='multipart/form-data')
    assert resp.status_code == 201
    assert resp.get_json()['file']['name'] == 'test.txt'


def test_list_files(client, auth_headers):
    client.post('/api/v1/files/folder', json={'name': 'MyFolder'}, headers=auth_headers)
    resp = client.get('/api/v1/files', headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()['files']) == 1


def test_rename_file(client, auth_headers):
    client.post('/api/v1/files/folder', json={'name': 'Old'}, headers=auth_headers)
    resp = client.put('/api/v1/files/1', json={'name': 'New'}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()['file']['name'] == 'New'


def test_delete_and_restore(client, auth_headers):
    client.post('/api/v1/files/folder', json={'name': 'Temp'}, headers=auth_headers)
    resp = client.delete('/api/v1/files/1', headers=auth_headers)
    assert resp.status_code == 200

    resp = client.get('/api/v1/trash', headers=auth_headers)
    assert len(resp.get_json()['files']) == 1

    resp = client.post('/api/v1/files/1/restore', headers=auth_headers)
    assert resp.status_code == 200


def test_share_file(client, auth_headers):
    data = {'file': (io.BytesIO(b'shared'), 'share.txt')}
    client.post('/api/v1/files', data=data, headers=auth_headers, content_type='multipart/form-data')

    resp = client.post('/api/v1/files/1/share', json={'expires_hours': 24}, headers=auth_headers)
    assert resp.status_code == 201
    code = resp.get_json()['share']['share_code']

    # 公开访问
    resp = client.get(f'/api/v1/share/{code}')
    assert resp.status_code == 200


def test_storage_stats(client, auth_headers):
    resp = client.get('/api/v1/files/stats', headers=auth_headers)
    assert resp.status_code == 200
    assert 'file_count' in resp.get_json()
