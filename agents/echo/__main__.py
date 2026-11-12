"""Chạy: uv run python -m agents.echo   (mặc định http://127.0.0.1:9100)"""

import os

import uvicorn

from agents.echo.server import build_app

HOST = os.getenv("ECHO_HOST", "127.0.0.1")
PORT = int(os.getenv("ECHO_PORT", "9100"))
PUBLIC_URL = os.getenv("ECHO_PUBLIC_URL", f"http://{HOST}:{PORT}")

if __name__ == "__main__":
    uvicorn.run(build_app(PUBLIC_URL), host=HOST, port=PORT)
