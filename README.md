# AP Copilot

Hệ **multi-agent** tự động đối soát và duyệt hoá đơn nhà cung cấp (Accounts Payable). Các thành phần:
- các agent nói chuyện với nhau bằng giao thức **A2A v1.0**;
- điều phối bằng **LangGraph**;
- agent gọi tool qua **MCP**;
- có **harness** gồm guardrail, budget, eval và test.

**Vấn đề.** Kế toán công nợ phải đọc hoá đơn (PDF hoặc ảnh scan), xác minh nhà cung cấp, rồi đối soát 3 bên (hoá đơn ↔ đơn mua hàng ↔ phiếu nhập kho), kiểm tra quy chế và trình duyệt. Tất cả đều làm thủ công.

**Giải pháp.** Mỗi bước do một agent chuyên trách đảm nhận. Các agent là service độc lập, khám phá nhau qua Agent Card và giao việc qua A2A Task. Orchestrator điều phối, chạy song song các bước kiểm tra, và dừng chờ người duyệt (human-in-the-loop) khi khoản chi lớn hoặc có rủi ro.

> 🚧 Đang build theo sprint 14 ngày. Tiến độ xem ở [Milestones](../../milestones) và `docs/learning-log.md`.
> 📐 Kiến trúc và luồng code chi tiết: **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**
> 📚 Bài học (dạy lại được): **[Bài 1: Bức tranh lớn: multi-agent, A2A, MCP, AP Copilot](docs/lessons/01-buc-tranh-lon.md)**

## Kiến trúc mục tiêu

```
UI ⇄ Orchestrator (LangGraph: fan-out · HITL interrupt · Postgres checkpointer)
        │  A2A (JSON-RPC + SSE)
        ├─► Extraction Agent  (Docling OCR + structured output + validate bằng code)
        ├─► Vendor Agent      (LangChain create_agent + MCP tools)
        ├─► Matching Agent    (3-way match PO/GRN/Invoice bằng Python)
        └─► Policy Agent      (RAG, viết bằng framework khác → chứng minh interop)
```

## Trạng thái

| Ngày | Nội dung | Trạng thái |
|---|---|---|
| D1 | Hello A2A: Echo Agent (LangGraph bọc trong A2A server), CLI, test in-process, CI | ✅ |
| D2 | ERP giả + bộ sinh hoá đơn + MCP servers | ⏳ |

## Chạy thử (Ngày 1)

Yêu cầu: Python 3.12 và [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run pytest -q                       # unit + A2A integration (in-process, không cần mạng)

uv run python -m agents.echo           # terminal 1: server tại http://127.0.0.1:9100
uv run python -m scripts.a2a_cli card http://127.0.0.1:9100
uv run python -m scripts.a2a_cli send http://127.0.0.1:9100 "xin   chào   A2A"
```

Kết quả streaming mẫu:
```
  <task>
  [TASK_STATE_WORKING]
  [TASK_STATE_WORKING] ✓ xong bước normalize
  [TASK_STATE_WORKING] ✓ xong bước respond
  <artifact_update>
  [TASK_STATE_COMPLETED]
final_state: TASK_STATE_COMPLETED
artifact   : Echo: xin chào A2A
```

## Cấu trúc

```
agents/echo/     graph.py (LangGraph) · executor.py (cầu nối A2A) · server.py (Agent Card + routes)
libs/            a2a_utils.py: client A2A dùng chung
scripts/         a2a_cli.py
tests/           test graph + test A2A end-to-end in-process
docs/            learning-log · war-stories · flashcards · adr/
```

## Stack
`a2a-sdk` 1.3 · LangGraph 1.2 · LangChain · Starlette/uvicorn · Postgres + pgvector · uv · ruff · pytest · GitHub Actions
