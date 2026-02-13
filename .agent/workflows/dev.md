---
description: How to run the LandWatch AI development server
---

## Steps

// turbo-all

1. Install Python dependencies:
```
pip install fastapi uvicorn jinja2 python-multipart aiofiles
```

2. Run the development server:
```
cd c:\LandWatchAi && python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

3. Open browser to http://localhost:8000
