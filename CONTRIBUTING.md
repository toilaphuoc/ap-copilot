# Quy ước làm việc

- **Branch**: `<type>/dNN-<mô-tả>`, ví dụ `feat/d03-extraction-agent`, `fix/d05-a2a-timeout`.
- **Commit**: Conventional Commits, ví dụ `feat(extraction): add arithmetic validation node`.
- **PR**: ghi What / Why / How tested. Squash merge. CI phải xanh.
- **Trước khi commit**: `uv run ruff check . && uv run ruff format . && uv run pytest -q`. Pre-commit sẽ tự chạy ruff.
- **Secrets**: chỉ commit `.env.example`. Không bao giờ commit `.env`.
- **Quy tắc vàng**: không merge dòng code nào mình không giải thích được.
