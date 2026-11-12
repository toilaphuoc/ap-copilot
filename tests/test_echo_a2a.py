"""Integration test qua giao thức A2A thật (JSON-RPC + SSE), chạy in-process.

httpx.ASGITransport gửi request thẳng vào Starlette app, không mở cổng mạng.
Nhờ vậy test nhanh, ổn định và chạy được trong CI. Đây là viên gạch đầu tiên của test harness.
"""

import httpx
import pytest

from agents.echo.server import build_app
from libs.a2a_utils import TaskSummary, fetch_card, send_text

BASE = "http://testserver"


@pytest.fixture
async def http():
    transport = httpx.ASGITransport(app=build_app(BASE))
    async with httpx.AsyncClient(transport=transport, base_url=BASE) as client:
        yield client


async def test_agent_card_is_discoverable(http):
    card = await fetch_card(BASE, http)
    assert card.name == "Echo Agent"
    assert card.capabilities.streaming is True
    assert [s.id for s in card.skills] == ["echo"]


@pytest.mark.parametrize("streaming", [True, False])
async def test_send_message_completes_with_artifact(http, streaming):
    card = await fetch_card(BASE, http)
    summary = TaskSummary()
    async for event in send_text(card, "xin   chào   A2A", http, streaming=streaming):
        summary.add(event)

    assert summary.final_state == "TASK_STATE_COMPLETED"
    assert "Echo: xin chào A2A" in summary.artifacts
    if streaming:
        # mỗi node của LangGraph → một status update
        assert summary.progress == ["✓ xong bước normalize", "✓ xong bước respond"]
