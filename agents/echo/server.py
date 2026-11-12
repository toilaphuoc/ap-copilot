"""Agent Card + Starlette app cho Echo Agent."""

from __future__ import annotations

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from starlette.applications import Starlette

from agents.echo.executor import EchoAgentExecutor


def build_agent_card(base_url: str) -> AgentCard:
    """'Danh thiếp' của agent, phục vụ tại /.well-known/agent-card.json.

    Client đọc card để biết agent làm được gì (skills), nói chuyện ở đâu
    (supported_interfaces) và có hỗ trợ streaming không (capabilities).
    """
    return AgentCard(
        name="Echo Agent",
        description="Agent mẫu Ngày 1: chạy một LangGraph 2 bước và trả lại tin nhắn.",
        version="0.1.0",
        capabilities=AgentCapabilities(streaming=True),
        supported_interfaces=[
            AgentInterface(url=base_url, protocol_binding="JSONRPC", protocol_version="1.0"),
        ],
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=[
            AgentSkill(
                id="echo",
                name="Echo",
                description="Chuẩn hoá khoảng trắng và trả lại tin nhắn.",
                tags=["demo", "echo"],
                examples=["xin   chào   A2A"],
            ),
        ],
    )


def build_app(base_url: str) -> Starlette:
    card = build_agent_card(base_url)
    handler = DefaultRequestHandler(
        agent_executor=EchoAgentExecutor(),
        task_store=InMemoryTaskStore(),  # Ngày 12: thay bằng store Postgres (task sống qua restart)
        agent_card=card,
    )
    routes = [*create_agent_card_routes(card), *create_jsonrpc_routes(handler, "/")]
    return Starlette(routes=routes)
