
#!/bin/bash
uvicorn app.processController:app --host 0.0.0.0 --port ${PORT:-8000}
