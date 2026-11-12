"""Tiện ích client A2A dùng chung (CLI, test, và sau này là orchestrator)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass, field

import httpx
from a2a.client import A2ACardResolver, ClientConfig, create_client
from a2a.helpers import get_artifact_text, get_message_text, new_text_message
from a2a.types import AgentCard, Role, SendMessageRequest, StreamResponse, TaskState


async def fetch_card(base_url: str, http: httpx.AsyncClient) -> AgentCard:
    """Discovery: đọc Agent Card ở /.well-known/agent-card.json."""
    return await A2ACardResolver(http, base_url).get_agent_card()


async def send_text(
    card: AgentCard, text: str, http: httpx.AsyncClient, *, streaming: bool = True
) -> AsyncIterator[StreamResponse]:
    """Gửi một tin nhắn text và yield từng sự kiện server trả về.

    streaming=True  → SendStreamingMessage (SSE): nhận task, status update, artifact lần lượt.
    streaming=False → SendMessage: thường chỉ nhận một Task cuối cùng.
    """
    # create_client là coroutine trong a2a-sdk 1.x (nó tự chọn transport theo card) → phải await.
    client = await create_client(card, ClientConfig(streaming=streaming, httpx_client=http))
    request = SendMessageRequest(message=new_text_message(text, role=Role.ROLE_USER))
    try:
        async for event in client.send_message(request):
            yield event
    finally:
        await client.close()


@dataclass
class TaskSummary:
    """Gom các sự kiện stream thành kết quả dễ đọc / dễ assert trong test."""

    task_id: str = ""
    final_state: str = ""
    progress: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)

    def add(self, event: StreamResponse) -> None:
        kind = event.WhichOneof("payload")
        if kind == "task":
            self.task_id = event.task.id
            self.final_state = TaskState.Name(event.task.status.state)
            self.artifacts += [get_artifact_text(a) for a in event.task.artifacts]
        elif kind == "status_update":
            self.task_id = event.status_update.task_id
            self.final_state = TaskState.Name(event.status_update.status.state)
            if event.status_update.status.HasField("message"):
                self.progress.append(get_message_text(event.status_update.status.message))
        elif kind == "artifact_update":
            self.artifacts.append(get_artifact_text(event.artifact_update.artifact))
        elif kind == "message":
            self.artifacts.append(get_message_text(event.message))
