import urllib.request
import urllib.error
import json
import uuid
import sys
import os

BASE = 'http://localhost:8000/api/v1'

def post(url, data, token=None):
    headers = {'Content-Type': 'application/json'}
    if token: headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(f'{BASE}{url}', data=json.dumps(data).encode(), headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode())

def get(url, token=None):
    headers = {}
    if token: headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(f'{BASE}{url}', headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.status, json.loads(resp.read().decode())

def delete(url, token=None):
    headers = {}
    if token: headers['Authorization'] = f'Bearer {token}'
    req = urllib.request.Request(f'{BASE}{url}', headers=headers)
    req.get_method = lambda: 'DELETE'
    with urllib.request.urlopen(req) as resp:
        return resp.status, None

def test_user_data_isolation():
    print('--- User A & User B Setup ---')
    user_a_email = f'user_a_{uuid.uuid4().hex[:6]}@example.com'
    user_b_email = f'user_b_{uuid.uuid4().hex[:6]}@example.com'
    pwd = 'Password123!'

    post('/auth/register', {'email': user_a_email, 'password': pwd})
    _, a_login = post('/auth/login', {'email': user_a_email, 'password': pwd})
    token_a = a_login['access_token']

    post('/auth/register', {'email': user_b_email, 'password': pwd})
    _, b_login = post('/auth/login', {'email': user_b_email, 'password': pwd})
    token_b = b_login['access_token']

    print('--- User A Creates a PRIVATE Problem ---')
    _, prob_a = post('/problems', {
        'title': 'User A Confidential Financial Audit',
        'description': 'Proprietary internal company audit reports.',
        'urgency': 'high',
        'is_public': False # Private
    }, token=token_a)
    pub_id_a = prob_a['public_id']
    prob_id_a = prob_a['id']
    print(f'User A private problem created: {pub_id_a}')

    print('--- User A Uploads Confidential File ---')
    boundary = '----Boundary' + uuid.uuid4().hex
    body = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="confidential.txt"\r\n'
        f'Content-Type: text/plain\r\n\r\n'
        f'CONFIDENTIAL_DATA_FOR_USER_A_ONLY\r\n'
        f'--{boundary}--\r\n'
    ).encode()
    upload_req = urllib.request.Request(
        f'{BASE}/problems/{pub_id_a}/files',
        data=body,
        headers={
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Authorization': f'Bearer {token_a}'
        }
    )
    with urllib.request.urlopen(upload_req) as resp:
        file_a = json.loads(resp.read().decode())
        file_id_a = file_a['id']
    print(f'User A uploaded file: {file_id_a}')

    print('--- Test 1: User B tries to view User A private problem ---')
    try:
        get(f'/problems/{pub_id_a}', token=token_b)
        print('FAIL: User B should NOT access User A private problem!')
        return False
    except urllib.error.HTTPError as e:
        print(f'PASS: User B blocked from private problem ({e.code} {e.reason})')

    print('--- Test 2: User B tries to download User A private file ---')
    try:
        get(f'/files/{file_id_a}/download', token=token_b)
        print('FAIL: User B should NOT download User A private file!')
        return False
    except urllib.error.HTTPError as e:
        print(f'PASS: User B blocked from downloading private file ({e.code} {e.reason})')

    print('--- Test 3: User B tries to delete User A file ---')
    try:
        delete(f'/files/{file_id_a}', token=token_b)
        print('FAIL: User B should NOT delete User A file!')
        return False
    except urllib.error.HTTPError as e:
        print(f'PASS: User B blocked from deleting User A file ({e.code} {e.reason})')

    print('--- Test 4: User A gets room and User B tries to enter User A private room ---')
    _, room_a = get(f'/problems/{pub_id_a}/room', token=token_a)
    room_id_a = room_a['id']

    try:
        get(f'/rooms/{room_id_a}/messages', token=token_b)
        print('FAIL: User B should NOT access private room messages!')
        return False
    except urllib.error.HTTPError as e:
        print(f'PASS: User B blocked from private room messages ({e.code} {e.reason})')

    print('--- Test 5: User B tries to post in User A private room ---')
    try:
        post(f'/rooms/{room_id_a}/messages', {'content': 'Intruder message'}, token=token_b)
        print('FAIL: User B should NOT post in private room!')
        return False
    except urllib.error.HTTPError as e:
        print(f'PASS: User B blocked from posting in private room ({e.code} {e.reason})')

    print('\n*** USER DATA ISOLATION & IDOR TESTS 100% PASS ***')
    return True

if __name__ == '__main__':
    test_user_data_isolation()

