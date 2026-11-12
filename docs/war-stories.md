# War stories

> Mẫu: Bối cảnh · Triệu chứng · Root cause · Fix · Kết quả · Bài học

### #1 `create_client` không được await (D01)
- **Bối cảnh**: viết client A2A theo tutorial cũ hoặc theo phản xạ (đối tượng factory thường là sync).
- **Triệu chứng**: `TypeError: object NoneType can't be used in 'await' expression` ở `client.close()`, test streaming và non-streaming đều fail.
- **Root cause**: trong `a2a-sdk` 1.x, `create_client` là coroutine (nó resolve card và chọn transport theo `supportedInterfaces`). Biến `client` thực chất là một coroutine object.
- **Fix**: `client = await create_client(card, ClientConfig(...))`. Kiểm tra lại bằng `inspect.iscoroutinefunction`.
- **Bài học**: SDK của giao thức mới thay đổi API rất nhanh. Phải **đọc signature thật của version đang cài** (`inspect.signature`) thay vì tin tutorial hay trí nhớ. Có test integration bắt được lỗi ngay ngày đầu.

### #2 Chạy script trong thư mục con bị `ModuleNotFoundError: libs` (D01)
- **Root cause**: `python scripts/a2a_cli.py` đặt `scripts/` lên `sys.path`, không phải thư mục gốc repo.
- **Fix**: chạy dạng module `python -m scripts.a2a_cli`; pytest cấu hình `pythonpath = ["."]`.
