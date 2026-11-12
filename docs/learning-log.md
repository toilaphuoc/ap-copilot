# Learning log

## D01 · 2026-11-12: Hello A2A

**Đã làm**
- Echo Agent: LangGraph 2 node (`normalize → respond`) bọc trong `AgentExecutor`, phục vụ bằng Starlette.
- Client CLI: đọc Agent Card, gửi `SendStreamingMessage` và `SendMessage`.
- Test A2A end-to-end in-process (`httpx.ASGITransport`), không cần mở cổng.

**Học được**
- **Agent Card** (`/.well-known/agent-card.json`) là "danh thiếp". Ở v1.0, endpoint nằm trong `supportedInterfaces[]` (url + `protocolBinding` + `protocolVersion`), không còn field `url` đơn.
- **Task lifecycle** tôi quan sát được khi stream: `task` (SUBMITTED) → `WORKING` (mỗi node một status update) → `artifact_update` → `COMPLETED`.
- **Message và Artifact**: status message là "tiến độ", artifact là "sản phẩm" của task, lấy lại được bằng `GetTask`.
- `a2a-sdk` 1.x dùng **protobuf** cho types (`StreamResponse.WhichOneof("payload")`), và `create_client` là **coroutine**.
- Reducer `Annotated[list, operator.add]`: các node trả `["tên"]` thì LangGraph nối list lại, không ghi đè.
- Gọi JSON-RPC thô cũng được: `method: "SendMessage"`, role `ROLE_USER`. Đây là bằng chứng A2A chỉ là HTTP + JSON, không gắn với framework nào.

**Tự hỏi và trả lời**
1. *Vòng đời A2A task?* SUBMITTED → WORKING → (INPUT_REQUIRED / AUTH_REQUIRED ↔ WORKING) → COMPLETED / FAILED / CANCELED / REJECTED.
2. *Vì sao A2A coi agent là "opaque"?* Bên gọi chỉ biết card và hợp đồng dữ liệu, không biết framework, prompt hay model bên trong. Nhờ đó các team và vendor độc lập, thay ruột mà không phá bên gọi.
3. *MCP và A2A?* MCP nối agent với tool/dữ liệu (dọc, agent điều khiển tool). A2A nối agent với agent (ngang hàng, task dài, có trạng thái).

**Còn mơ hồ (ôn lại D2/D4)**
- Multi-turn: gửi tiếp message với cùng `taskId`/`contextId` khi `INPUT_REQUIRED` thì `context.current_task` có giá trị. Sẽ thử ở D3.
- Push notification config: để dành cho D3 (file lớn).
