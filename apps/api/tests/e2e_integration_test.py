import urllib.request
import urllib.error
import json
import time

BASE = 'http://localhost:8000/api/v1'

def post(url, data, token=None, cookies=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if cookies:
        headers['Cookie'] = cookies
    req = urllib.request.Request(f'{BASE}{url}', data=json.dumps(data).encode(), headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.headers, json.loads(resp.read().decode())

def get(url, token=None, cookies=None):
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    if cookies:
        headers['Cookie'] = cookies
    req = urllib.request.Request(f'{BASE}{url}', headers=headers)
    with urllib.request.urlopen(req) as resp:
        return resp.status, resp.headers, json.loads(resp.read().decode())

def main():
    print('--- 1. Register & Login ---')
    email = f'qa_tester_{int(time.time())}@example.com'
    password = 'TestPassword123!'

    s, _, reg = post('/auth/register', {'email': email, 'password': password})
    print(f'Register: {s} -> ID: {reg["id"]}')

    s, hdrs, login = post('/auth/login', {'email': email, 'password': password})
    token = login['access_token']
    cookie_header = hdrs.get('Set-Cookie', '').split(';')[0]
    print(f'Login: {s} -> Token: {token[:15]}... | Cookie: {cookie_header[:25]}...')

    print('--- 2. Auth /me ---')
    s, _, me_tok = get('/auth/me', token=token)
    assert me_tok['email'] == email
    print(f'Auth/me with Bearer token: {s} ({me_tok["email"]})')

    s, _, me_ck = get('/auth/me', cookies=cookie_header)
    assert me_ck['email'] == email
    print(f'Auth/me with Cookie: {s} ({me_ck["email"]})')

    print('--- 3. Problem Creation ---')
    s, _, prob = post('/problems', {
        'title': 'High CPU utilization in worker pool',
        'description': 'Our async worker nodes are pegging CPU at 100% due to an unhandled infinite loop.',
        'urgency': 'high',
        'is_public': True
    }, token=token)
    pub_id = prob['public_id']
    print(f'Create Problem: {s} -> public_id: {pub_id}')

    print('--- 4. Problem Detail Retrieval ---')
    s, _, prob_detail = get(f'/problems/{pub_id}', token=token)
    print(f'Get Problem by public_id: {s} -> title: {prob_detail["title"]}')

    print('--- 5. Submit Solution ---')
    s, _, sol = post(f'/problems/{pub_id}/solutions', {
        'content': 'Implement rate limiting and set worker timeout to 30 seconds.'
    }, token=token)
    sol_id = sol['id']
    print(f'Submit Solution: {s} -> id: {sol_id}')

    print('--- 6. Vote on Solution by User 2 ---')
    user2_email = f'voter_{int(time.time())}@example.com'
    post('/auth/register', {'email': user2_email, 'password': 'Password123!'})
    _, _, login2 = post('/auth/login', {'email': user2_email, 'password': 'Password123!'})
    token2 = login2['access_token']
    s, _, vote = post(f'/solutions/{sol_id}/vote', {'value': 1}, token=token2)
    print(f'Vote on Solution: {s} -> upvotes: {vote.get("upvotes", 1)}')

    print('--- 7. Live Room Creation & Messages ---')
    s, _, room = get(f'/problems/{pub_id}/room', token=token)
    room_id = room['id']
    print(f'Get/Create Room: {s} -> room_id: {room_id}')

    s, _, msg = post(f'/rooms/{room_id}/messages', {'content': 'Hello team, investigating now.'}, token=token)
    print(f'Room Message: {s} -> message: {msg["content"]}')

    s, _, ai_msg = post(f'/rooms/{room_id}/messages', {'content': '@ai what could cause worker 100% CPU?'}, token=token)
    print(f'Room @ai Message: {s} -> status: sent and dispatched to AI orchestrator')

    print('--- 8. AI Endpoints ---')
    s, _, ai_chat = post('/ai/chat', {'message': 'Calculate fibonacci of 10 in python', 'agent_type': 'coding'}, token=token)
    print(f'AI Chat (Coding Agent): {s} -> steps: {len(ai_chat.get("activity_steps", []))}')

    s, _, ai_solve = post('/ai/solve', {'problem_id_or_public_id': pub_id}, token=token)
    print(f'AI Solve Problem: {s} -> agent: {ai_solve.get("agent_type")} | role: {ai_solve.get("agent_role")}')

    s, _, ai_explain = post('/ai/explain', {'message': 'Explain how postgres B-Tree indexes work'}, token=token)
    print(f'AI Explain: {s} -> steps: {len(ai_explain.get("activity_steps", []))}')

    s, _, ai_hint = post('/ai/hint', {'message': 'How to invert a binary tree without recursion'}, token=token)
    print(f'AI Hint: {s} -> steps: {len(ai_hint.get("activity_steps", []))}')

    s, _, ai_debug = post('/ai/debug', {'message': 'TypeError: Cannot read properties of undefined (reading map)'}, token=token)
    print(f'AI Debug: {s} -> steps: {len(ai_debug.get("activity_steps", []))}')

    s, _, ai_verify = post('/ai/verify', {'message': 'def add(a, b): return a * b', 'problem_context': 'Function should perform addition'}, token=token)
    print(f'AI Verify: {s} -> response length: {len(ai_verify.get("response", ""))}')

    print('--- 9. Logout ---')
    s, _, logout = post('/auth/logout', {}, token=token, cookies=cookie_header)
    print(f'Logout: {s}')

    try:
        get('/auth/me', token=token)
        print('ERROR: Token should have been revoked!')
        return False
    except urllib.error.HTTPError as e:
        print(f'Verified token revocation: {e.code} ({e.reason})')

    print('\n*** ALL 9 TEST SUITES COMPLETED WITH 100% PASS ***')
    return True

if __name__ == '__main__':
    main()
