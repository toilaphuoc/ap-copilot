"""Cầu nối LangGraph ↔ A2A.

A2A server (DefaultRequestHandler) nhận JSON-RPC `SendMessage` / `SendStreamingMessage`,
dựng RequestContext rồi gọi `execute()`. Nhiệm vụ của executor:
  1. Tạo (hoặc lấy lại) Task và đưa vào event_queue.
  2. Phát status update khi đang làm việc → client streaming thấy tiến độ.
  3. Gắn kết quả thành Artifact.
  4. Kết thúc bằng một trạng thái terminal (COMPLETED / FAILED / ...).
"""

from __future__ import annotations

from a2a.helpers import get_message_text, new_task_from_user_message, new_text_part
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState

from agents.echo.graph import graph


class EchoAgentExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # (1) Task: tin nhắn tiếp nối cùng task (multi-turn) thì đã có current_task.
        task = context.current_task
        if task is None:
            task = new_task_from_user_message(context.message)
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task.id, task.context_id)
        await updater.start_work()  # → TASK_STATE_WORKING

        user_text = get_message_text(context.message)

        # (2) stream_mode="updates": mỗi node chạy xong trả {tên_node: phần_state_thay_đổi}.
        #     Ta chuyển mỗi bước của graph thành một status update của A2A.
        final: dict = {}
        async for update in graph.astream({"text": user_text}, stream_mode="updates"):
            for node_name, delta in update.items():
                final.update(delta)
                await updater.update_status(
                    state=TaskState.TASK_STATE_WORKING,
                    message=updater.new_agent_message([new_text_part(f"✓ xong bước {node_name}")]),
                )

        # (3) Kết quả là artifact, không phải message: artifact là "sản phẩm" của task,
        #     client có thể lấy lại bằng GetTask sau này.
        await updater.add_artifact(parts=[new_text_part(final["reply"])], name="echo_reply")

        # (4) Trạng thái terminal.
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        # Echo chạy tức thì nên chỉ cần chuyển trạng thái. Agent chạy lâu (OCR) sẽ phải
        # đặt cờ huỷ và kiểm tra cờ giữa các node.
        task = context.current_task
        if task is not None:
            await TaskUpdater(event_queue, task.id, task.context_id).cancel()
