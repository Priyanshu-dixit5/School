"""Quick integration tests for the job portal."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app()

with app.test_client() as c:
    r = c.get('/admin/login')
    assert r.status_code == 200

    import re
    csrf_match = re.search(r'name="csrf_token" value="([^"]+)"', r.data.decode())
    token = csrf_match.group(1) if csrf_match else ''

    r = c.post('/admin/login', data={
        'username': 'admin',
        'password': 'admin123',
        'csrf_token': token,
    }, follow_redirects=True)
    assert r.status_code == 200

    r = c.get('/api/jobs')
    assert r.status_code == 200
    assert r.json['total'] >= 2

    r = c.get('/careers')
    assert r.status_code == 200
    assert b'Trained Graduate Teacher' in r.data

    r = c.get('/careers/trained-graduate-teacher')
    assert r.status_code == 200

    print('All integration tests passed!')
