def test_create_notebook(client, auth_headers):
    resp = client.post('/api/v1/notebooks', json={'name': 'Work'}, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()['notebook']['name'] == 'Work'


def test_create_note(client, auth_headers):
    resp = client.post('/api/v1/notes', json={
        'title': 'Test Note', 'content': '# Hello',
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()['note']['title'] == 'Test Note'


def test_update_note(client, auth_headers):
    client.post('/api/v1/notes', json={'title': 'Draft', 'content': ''}, headers=auth_headers)
    resp = client.put('/api/v1/notes/1', json={'title': 'Final', 'content': 'Done'}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()['note']['title'] == 'Final'


def test_search_notes(client, auth_headers):
    client.post('/api/v1/notes', json={'title': 'Python Tips', 'content': 'use list comp'}, headers=auth_headers)
    client.post('/api/v1/notes', json={'title': 'Cooking', 'content': 'make pasta'}, headers=auth_headers)

    resp = client.get('/api/v1/notes?search=Python', headers=auth_headers)
    assert len(resp.get_json()['notes']) == 1


def test_note_versions(client, auth_headers):
    client.post('/api/v1/notes', json={'title': 'V', 'content': 'v1'}, headers=auth_headers)
    client.put('/api/v1/notes/1', json={'content': 'v2'}, headers=auth_headers)

    resp = client.get('/api/v1/notes/1/versions', headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.get_json()['versions']) >= 2


def test_create_tag(client, auth_headers):
    resp = client.post('/api/v1/tags', json={'name': 'important'}, headers=auth_headers)
    assert resp.status_code == 201


def test_delete_note(client, auth_headers):
    client.post('/api/v1/notes', json={'title': 'To Delete'}, headers=auth_headers)
    resp = client.delete('/api/v1/notes/1', headers=auth_headers)
    assert resp.status_code == 200


def test_export_note(client, auth_headers):
    client.post('/api/v1/notes', json={'title': 'Export', 'content': '# Test'}, headers=auth_headers)
    resp = client.get('/api/v1/notes/1/export/markdown', headers=auth_headers)
    assert resp.status_code == 200
    assert b'# Test' in resp.data
