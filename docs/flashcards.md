# Flashcards (ôn lại: D01 → D02, D04, D08, D14)

| Hỏi | Đáp |
|---|---|
| Agent Card nằm ở đâu, chứa gì? | `/.well-known/agent-card.json`: name, description, version, `supportedInterfaces[]`, capabilities (streaming, push…), skills, securitySchemes, default input/output modes |
| Tên method A2A v1.0 cho gửi tin có stream? | `SendStreamingMessage` (v0.3 là `message/stream`), trả về SSE |
| Các trạng thái Task? | SUBMITTED, WORKING, INPUT_REQUIRED, AUTH_REQUIRED, COMPLETED, FAILED, CANCELED, REJECTED (prefix `TASK_STATE_`) |
| Message khác Artifact? | Message: một lượt giao tiếp hoặc tiến độ. Artifact: sản phẩm đầu ra của task |
| 4 loại event trong StreamResponse? | task, message, status_update, artifact_update |
| Vai trò của `AgentExecutor`? | Chứa logic agent: đọc RequestContext, đẩy Task / status / artifact vào EventQueue, kết thúc ở trạng thái terminal |
| Reducer trong LangGraph để làm gì? | Quy định cách gộp khi node ghi vào một field, ví dụ `operator.add` để nối list |
| MCP và A2A một câu? | MCP: agent ↔ tool (dọc). A2A: agent ↔ agent (ngang, opaque, task dài) |
