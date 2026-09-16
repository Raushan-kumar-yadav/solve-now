import urllib.request
import urllib.error
import json
import uuid
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ai.rag.document_processor import DocumentProcessor
from services.ai.rag.retriever import RAGRetriever

def test_file_and_rag_pipeline():
    # 1. Login user
    login_req = urllib.request.Request(
        'http://localhost:8000/api/v1/auth/login',
        data=json.dumps({'email': 'demo_user@example.com', 'password': 'Password123!'}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(login_req) as resp:
        token = json.loads(resp.read().decode())['access_token']

    # 2. Create problem
    prob_req = urllib.request.Request(
        'http://localhost:8000/api/v1/problems',
        data=json.dumps({
            'title': 'RAG and File Verification Problem',
            'description': 'Testing full file lifecycle and RAG retrieval.',
            'urgency': 'normal',
            'is_public': True
        }).encode(),
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
    )
    with urllib.request.urlopen(prob_req) as resp:
        prob = json.loads(resp.read().decode())
        pub_id = prob['public_id']
        print('Created problem:', pub_id)

    # 3. Upload file using multipart/form-data
    boundary = '----WebKitFormBoundary' + uuid.uuid4().hex
    content = b'This is a test document.\nSOLVENOW_RAG_TEST_92841 is the secret project verification code.\nEnd of document.'
    header = (
        f'--{boundary}\r\n'
        f'Content-Disposition: form-data; name="file"; filename="secret_rag_doc.txt"\r\n'
        f'Content-Type: text/plain\r\n\r\n'
    ).encode()
    footer = f'\r\n--{boundary}--\r\n'.encode()
    body = header + content + footer

    upload_req = urllib.request.Request(
        f'http://localhost:8000/api/v1/problems/{pub_id}/files',
        data=body,
        headers={
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Authorization': f'Bearer {token}'
        }
    )
    with urllib.request.urlopen(upload_req) as resp:
        file_record = json.loads(resp.read().decode())
        file_id = file_record['id']
        print(f'Uploaded file: {file_id}, {file_record["original_name"]}, size: {file_record["size"]}')

    # 4. Download file
    dl_req = urllib.request.Request(
        f'http://localhost:8000/api/v1/files/{file_id}/download',
        headers={'Authorization': f'Bearer {token}'}
    )
    with urllib.request.urlopen(dl_req) as resp:
        dl_content = resp.read()
        print('Downloaded file content:\n', dl_content.decode())
        assert b'SOLVENOW_RAG_TEST_92841' in dl_content
        print('Integrity check: SOLVENOW_RAG_TEST_92841 found in download!')

    # 5. Test RAG Chunking and Retrieval on this exact content
    raw_doc = dl_content.decode('utf-8')
    retriever = RAGRetriever(documents=[raw_doc])
    retrieved = retriever.search('What is SOLVENOW_RAG_TEST_92841?', top_k=2)
    print(f'RAG: Retrieved {len(retrieved)} relevant chunks.')
    assert any('SOLVENOW_RAG_TEST_92841' in c['content'] for c in retrieved)
    print('RAG Test: Successfully retrieved SOLVENOW_RAG_TEST_92841 chunk!')

    # 6. Delete file
    del_req = urllib.request.Request(
        f'http://localhost:8000/api/v1/files/{file_id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    del_req.get_method = lambda: 'DELETE'
    with urllib.request.urlopen(del_req) as resp:
        print('Delete file response status:', resp.status)

    # 7. Verify file no longer exists
    try:
        with urllib.request.urlopen(dl_req) as resp:
            print('ERROR: File still exists!')
            return False
    except urllib.error.HTTPError as e:
        print(f'Confirmed file deletion: {e.code} ({e.reason})')

    print('\n*** FILE & RAG PIPELINE VERIFIED SUCCESSFULLY WITH 100% PASS ***')
    return True

if __name__ == '__main__':
    test_file_and_rag_pipeline()
