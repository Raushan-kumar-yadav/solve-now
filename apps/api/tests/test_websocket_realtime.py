import asyncio
import json
import urllib.request
import websockets
import uuid

BASE = 'http://localhost:8000/api/v1'
WS_BASE = 'ws://localhost:8000/api/v1'

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

async def run_two_client_test():
    print('--- Setup User 1 and User 2 ---')
    u1_email = f'ws_user1_{uuid.uuid4().hex[:6]}@example.com'
    u2_email = f'ws_user2_{uuid.uuid4().hex[:6]}@example.com'
    pwd = 'Password123!'

    post('/auth/register', {'email': u1_email, 'password': pwd})
    _, l1 = post('/auth/login', {'email': u1_email, 'password': pwd})
    token1 = l1['access_token']

    post('/auth/register', {'email': u2_email, 'password': pwd})
    _, l2 = post('/auth/login', {'email': u2_email, 'password': pwd})
    token2 = l2['access_token']

    print('--- Create Problem & Room ---')
    _, prob = post('/problems', {
        'title': 'Realtime WebSocket Synchronization Test',
        'description': 'Testing multi-user WebSocket distribution over Redis.',
        'urgency': 'normal',
        'is_public': True
    }, token=token1)
    pub_id = prob['public_id']

    _, room = get(f'/problems/{pub_id}/room', token=token1)
    room_id = room['id']
    print(f'Room ID: {room_id}')

    print('--- Connect Client 2 via WebSocket ---')
    ws2_url = f'{WS_BASE}/ws/rooms/{room_id}?token={token2}'
    
    received_messages = []

    async with websockets.connect(ws2_url) as ws2:
        print('Client 2 connected to WebSocket!')
        await asyncio.sleep(0.5)

        # Now Client 1 posts a chat message to the room via REST API
        print('--- Client 1 sends message via API ---')
        msg_text = f'Hello from Client 1! UUID: {uuid.uuid4().hex}'
        post(f'/rooms/{room_id}/messages', {'content': msg_text}, token=token1)

        # Client 2 should receive the broadcast from Redis Pub/Sub in real time!
        print('--- Client 2 waiting for broadcast message ---')
        while True:
            raw = await asyncio.wait_for(ws2.recv(), timeout=5.0)
            data = json.loads(raw)
            print('Client 2 received event:', data.get('type'))
            if data.get('type') == 'message.created':
                received_payload = data['payload']
                print('Broadcast payload:', received_payload)
                assert received_payload['content'] == msg_text
                print('Verified! Client 2 received exact message sent by Client 1!')
                break

    print('\n*** TWO-CLIENT REALTIME WEBSOCKET & REDIS PUBSUB TEST PASSED 100% ***')
    return True

if __name__ == '__main__':
    asyncio.run(run_two_client_test())
