# start.sh
#!/bin/bash
source /home/ubuntu/backtrader-app/venv/bin/activate
exec uvicorn src.main:app --host 0.0.0.0 --port 8080
