import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
root_dir = backend_dir.parent

if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting NEXORA Backend Server...")
    print("   • Local URL:    http://127.0.0.1:8000")
    print("   • API Docs:     http://127.0.0.1:8000/docs")
    print("   • Health Check: http://127.0.0.1:8000/")
    print("=" * 60)
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

