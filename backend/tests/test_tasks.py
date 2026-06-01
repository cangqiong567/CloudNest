def test_create_column(client, auth_headers):
    resp = client.post('/api/v1/task-columns', json={'name': 'To Do'}, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()['column']['name'] == 'To Do'


def test_create_task(client, auth_headers):
    client.post('/api/v1/task-columns', json={'name': 'Backlog'}, headers=auth_headers)
    resp = client.post('/api/v1/tasks', json={
        'title': 'My Task', 'column_id': 1, 'priority': 2,
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.get_json()['task']['priority'] == 2


def test_move_task(client, auth_headers):
    client.post('/api/v1/task-columns', json={'name': 'Col1'}, headers=auth_headers)
    client.post('/api/v1/task-columns', json={'name': 'Col2'}, headers=auth_headers)
    client.post('/api/v1/tasks', json={'title': 'T', 'column_id': 1}, headers=auth_headers)

    resp = client.put('/api/v1/tasks/1/move', json={'column_id': 2, 'position': 0}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()['task']['column_id'] == 2


def test_task_stats(client, auth_headers):
    client.post('/api/v1/tasks', json={'title': 'A'}, headers=auth_headers)
    resp = client.get('/api/v1/tasks/stats', headers=auth_headers)
    assert resp.status_code == 200
    assert resp.get_json()['total'] == 1


def test_delete_task(client, auth_headers):
    client.post('/api/v1/tasks', json={'title': 'Del'}, headers=auth_headers)
    resp = client.delete('/api/v1/tasks/1', headers=auth_headers)
    assert resp.status_code == 200


def test_list_tasks(client, auth_headers):
    client.post('/api/v1/tasks', json={'title': 'T1'}, headers=auth_headers)
    client.post('/api/v1/tasks', json={'title': 'T2'}, headers=auth_headers)
    resp = client.get('/api/v1/tasks', headers=auth_headers)
    assert len(resp.get_json()['tasks']) == 2


def test_reorder_tasks(client, auth_headers):
    client.post('/api/v1/tasks', json={'title': 'A'}, headers=auth_headers)
    client.post('/api/v1/tasks', json={'title': 'B'}, headers=auth_headers)
    resp = client.put('/api/v1/tasks/reorder', json={
        'items': [{'id': 1, 'position': 2}, {'id': 2, 'position': 1}]
    }, headers=auth_headers)
    assert resp.status_code == 200
