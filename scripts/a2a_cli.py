"""CLI gọi bất kỳ A2A agent nào.

Ví dụ:
  uv run python -m scripts.a2a_cli card  http://127.0.0.1:9100
  uv run python -m scripts.a2a_cli send  http://127.0.0.1:9100 "xin   chào   A2A"
  uv run python -m scripts.a2a_cli send  http://127.0.0.1:9100 "xin chào" --no-stream
"""

from __future__ import annotations

import argparse
import asyncio
import sys

import httpx
from a2a.helpers import display_agent_card, get_message_text
from a2a.types import TaskState

from libs.a2a_utils import TaskSummary, fetch_card, send_text


async def cmd_card(url: str) -> None:
    async with httpx.AsyncClient(timeout=10) as http:
        card = await fetch_card(url, http)
        display_agent_card(card)


async def cmd_send(url: str, text: str, streaming: bool) -> int:
    async with httpx.AsyncClient(timeout=60) as http:
        card = await fetch_card(url, http)
        summary = TaskSummary()
        async for event in send_text(card, text, http, streaming=streaming):
            summary.add(event)
            kind = event.WhichOneof("payload")
            if kind == "status_update":
                status = event.status_update.status
                note = get_message_text(status.message) if status.HasField("message") else ""
                print(f"  [{TaskState.Name(status.state)}] {note}")
            else:
                print(f"  <{kind}>")
        print(f"\ntask_id    : {summary.task_id}\nfinal_state: {summary.final_state}")
        for a in summary.artifacts:
            print(f"artifact   : {a}")
        return 0 if summary.final_state == "TASK_STATE_COMPLETED" else 1


def main() -> int:
    p = argparse.ArgumentParser(description="A2A CLI")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("card")
    c.add_argument("url")
    s = sub.add_parser("send")
    s.add_argument("url")
    s.add_argument("text")
    s.add_argument("--no-stream", action="store_true")
    a = p.parse_args()
    if a.cmd == "card":
        asyncio.run(cmd_card(a.url))
        return 0
    return asyncio.run(cmd_send(a.url, a.text, streaming=not a.no_stream))


if __name__ == "__main__":
    sys.exit(main())
