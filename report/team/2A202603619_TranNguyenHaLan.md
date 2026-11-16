# Báo cáo cá nhân — 2A202603619_TranNguyenHaLan

## 1. Thông tin thành viên

- Họ tên: Trần Nguyễn Hà Lan
- MSSV: 2A202603619
- Email: lan.tnh233861@sis.hust.edu.vn
- GitHub: HaLanWS

## 2. Phần việc phụ trách

- **Vai trò:** Người 1 — Workflow & Kiểm thử nghiệp vụ.
- **Phụ trách chính:**
  - Triển khai toàn bộ kiến trúc Shape A (`src/lab8/shapes/workflow.py`).
  - Kiểm soát các ràng buộc nghiệp vụ: trễ giao, hỏng hàng, lọc bỏ policy cũ (`SHIP-LATE-OLD`), quy tắc lấy `max` thay vì cộng dồn khi thỏa mãn cả 2 điều kiện.
  - Xử lý các ranh giới bảo mật & độ tin cậy: đọc an toàn qua allowlist (`get_claim_view`), không leak PII/secret vào trace, truyền full quote vào cổng host (`durability.issue_refund`), không bắt ngoại lệ `InjectedCrash`.
  - Bổ sung test kiểm thử nghiệp vụ trong `src/tests/test_compensation.py`.

## 3. Đóng góp cụ thể

- **Commit kỹ thuật chính:**
  - Commit triển khai Workflow: `364b192` (`feat(workflow): implement deterministic workflow shape with full student test pass`).
- **Test đã thêm/sửa:**
  - Thêm test `test_workflow_stacking_max_not_sum` trong `src/tests/test_compensation.py` nhằm xác nhận quy tắc bồi thường: khi đơn vừa trễ hẹn vừa hỏng hàng thì bồi thường theo giá trị lớn nhất (`max`), tuyệt đối không cộng gộp hai khoản.
- **Quyết định kỹ thuật đưa ra:**
  - Xây dựng luồng thực thi thuần Python (deterministic) không dùng model để tính tiền, tuân thủ nguyên tắc Least Autonomous Working Shape.
  - Luôn truyền **full quote** vào `durability.issue_refund` để Host tự tính và trừ phần tiền đã hoàn trước đó (đáp ứng đúng T13 và T14).
  - Không bắt lỗi `InjectedCrash` để hệ thống kiểm thử tự động đo lường độ an toàn khi crash (Crash safety).
  - Sử dụng `lab8.shapes.common.finish()` để chuẩn hóa việc xuất `RunResult` và ghi trace đạt chuẩn Trace Contract v1.

## 4. Bằng chứng

- **Kết quả kiểm thử:**
  - Kiểm thử ma trận Student cho Workflow: `python -m pytest -q -m student -o addopts= -k workflow` đạt **62/62 passed (100%)**.
  - Kiểm thử Cổng Host: `python -m pytest -q` đạt **55/55 passed (100%)**.
  - Kiểm thử nghiệp vụ mới thêm: `python -m pytest -q tests/test_compensation.py` đạt **4/4 passed**.
  - Kiểm tra tính hợp lệ bằng công cụ nộp bài: `python -m lab8.check_submission` xác nhận `[ OK ] shape workflow: format đúng, 12/12 claim public pass ở seed 11`.
- **An toàn dữ liệu & Trace:**
  - Đã quét toàn bộ trace trong `src/traces/`, xác nhận `secret_leak_count = 0` và `pii_leak_count = 0`.

## 5. Công cụ AI đã dùng

- **Công cụ:** Trợ lý AI Antigravity (Gemini 3.8 Flash).
- **Mục đích sử dụng:**
  - Phân tích và hệ thống hóa các yêu cầu, hợp đồng dữ liệu từ `docs/contracts.md` và `docs/business_rules.md`.
  - Gợi ý cấu trúc điều hướng an toàn trong `workflow.py` (tương tác với `get_claim_view`, `lookup_order`, `compute_compensation`, `issue_refund`).
  - Hỗ trợ phân tích nguyên nhân lỗi môi trường trên Windows và xử lý phân biệt tài khoản Git khi push.
- **Cách tự kiểm tra kết quả:**
  - Tự chạy lệnh kiểm thử `pytest` trên cả test suite student và host.
  - Chạy script kiểm tra độc lập các file trace sinh ra để xác minh không rò rỉ secret/PII.
  - Chạy `python -m lab8.check_submission` để đối chiếu format đầu ra.

## 6. Tự đánh giá

- **Mức độ hoàn thành:** 100% phần việc được giao theo đúng tiến độ Checkpoint CP2 & CP3.
- **Đánh giá cá nhân:** Nắm vững sự khác biệt giữa kiến trúc luồng cố định (Workflow) và kiến trúc Agent tự chủ; hiểu rõ cơ chế bảo đảm idempotency và trần hoàn tiền qua cổng Host.
