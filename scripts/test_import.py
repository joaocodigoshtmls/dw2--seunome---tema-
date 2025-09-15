import sys
sys.path.append(r'c:\Users\Pass\Desktop\dw2')

print('PYTHON TEST START')
try:
    from backend.app import app
    print('IMPORT backend.app OK')
    try:
        from fastapi.testclient import TestClient
        client = TestClient(app)
        r = client.get('/health')
        print('GET /health ->', r.status_code, r.json())
    except Exception as e:
        print('TestClient not available or failed:', e)
except Exception as e:
    print('IMPORT_ERR', repr(e))
