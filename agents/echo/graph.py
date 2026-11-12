"""LangGraph nhỏ nhất có ý nghĩa: 2 node, state có kiểu, không cần LLM.

Mục đích của Ngày 1 là hiểu "khung" (state → node → edge) và cách bọc một graph
vào A2A, nên graph cố tình đơn giản và chạy deterministic (test không tốn tiền).
"""

from __future__ import annotations

import operator
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph


class EchoState(TypedDict, total=False):
    text: str  # input từ user
    normalized: str  # output của node normalize
    reply: str  # output cuối
    # Reducer operator.add: mỗi node trả về ["tên"] → LangGraph NỐI vào list thay vì ghi đè.
    steps: Annotated[list[str], operator.add]


def normalize(state: EchoState) -> EchoState:
    """Node 1: làm sạch input. Node chỉ trả về PHẦN state thay đổi."""
    cleaned = " ".join(state.get("text", "").split())
    return {"normalized": cleaned, "steps": ["normalize"]}


def respond(state: EchoState) -> EchoState:
    """Node 2: tạo câu trả lời từ state do node trước để lại."""
    text = state["normalized"]
    reply = f"Echo: {text}" if text else "Echo: (tin nhắn rỗng)"
    return {"reply": reply, "steps": ["respond"]}


def build_graph():
    g = StateGraph(EchoState)
    g.add_node("normalize", normalize)
    g.add_node("respond", respond)
    g.add_edge(START, "normalize")
    g.add_edge("normalize", "respond")
    g.add_edge("respond", END)
    return g.compile()


graph = build_graph()
