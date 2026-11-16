# Báo cáo nhóm — Lab 8 LogiX-VN

Tối đa 5 trang ngoài phụ lục. Số liệu lấy từ file trong `src/reports/`, không chép tay từ terminal.

## 1. Thông tin nhóm

- Tên nhóm: ABC
- Thành viên: xem `TEAM.md`
- Commit chốt (trùng `report/team/decision_adr.md`):

## 2. Mục tiêu và cách tiếp cận

Nhóm xử lý claim hoàn phí của LogiX-VN qua bốn shape dùng cùng claim, seed, world state, pricing và evaluator. Nhóm chia ba shape cần viết cho ba thành viên, thành viên còn lại phụ trách integration, test, crash, benchmark và hồ sơ. Thứ tự thực hiện là đọc contract, viết shape song song, chạy student matrix, kiểm tra durability/security, benchmark và chọn kiến trúc.

...

## 3. Giải pháp

Workflow dùng các bước Python cố định; single dùng ReAct nhưng model chỉ được chọn read tool; orchestrator dùng investigator read-only và handoff allowlist. Cả ba shape tính quote bằng code, truyền full quote cho host và để host kiểm approval, policy, cap theo order và idempotency. Handoff được sanitize, không truyền secret/header/full claim row; trace ghi event đã allowlist và không ghi PII hay secret.

...

## 4. Kết quả

Kết quả benchmark public: workflow 1.000/1.000, variance 0.000000, cost/success 27.86, steps 2.50; single 1.000/1.000, 0.000000, 30.27, 7.21; orchestrator 1.000/1.000, 0.000000, 46.43, 3.71; swarm 0.986/0.929, variance 0.000816, cost/success 49.57, 2.80. Crash safety đạt 20/20. Nhóm chọn workflow vì đạt độ chính xác như các shape đúng khác với chi phí thấp nhất.

...

Quyết định kiến trúc và lý do: xem `report/team/decision_adr.md`. Phiếu nghiên cứu và ablation: xem `report/team/research_card.md`.

## 5. Khó khăn và cách xử lý

Ban đầu ba shape còn stub nên student matrix fail; nhóm triển khai và merge lần lượt từng shape, sau đó chạy lại đến 248 passed. Benchmark có một miss có chủ đích của swarm ở seed 55; nhóm giữ nguyên kết quả vì đây là weakness của shape đối chứng, không sửa report bằng tay.

...

## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong `TEAM.md` và các báo cáo cá nhân `report/team/MSSV_HoTen.md`; nhóm cần điền tên, commit và test thực tế trước khi nộp.

## 7. Hạn chế và hướng cải thiện

MockLLM không phải model sản xuất, cost là mô phỏng và latency là `unavailable`. Public benchmark nhỏ và synthetic; kết luận có thể thay đổi trên hidden hoặc dữ liệu thật nếu claim mơ hồ, task có phần điều tra song song hoặc topology agent cải thiện pass rate đủ lớn để bù chi phí.

...

## 8. Tài liệu tham khảo

...
