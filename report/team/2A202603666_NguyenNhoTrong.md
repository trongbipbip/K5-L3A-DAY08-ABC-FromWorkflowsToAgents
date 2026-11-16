# 2A202603666_NguyenNhoTrong

## Thông tin thành viên

- Họ tên: Nguyễn Nho Trọng
- MSSV: 2A202603666
- Vai trò: Evaluation + report/integration

## Phần việc phụ trách

- Theo dõi tích hợp ba shape `workflow`, `single` và `orchestrator` sau khi các thành viên merge.
- Chạy student matrix, host test, crash suite và benchmark public.
- Kiểm tra kết quả CP2–CP5 và tổng hợp bằng chứng nộp bài.
- Hoàn thiện `TEAM.md`, `decision_adr.md`, `research_card.md` và `group_report.md`.

## Đóng góp cụ thể

- Xác nhận student matrix đạt `248 passed`.
- Xác nhận host test đạt `303 passed`.
- Chạy crash suite đạt `crash_safety 20/20`.
- Chạy benchmark bốn shape trên 14 claim và 5 seed.
- Tổng hợp kết quả benchmark: `workflow`, `single` và `orchestrator` đạt pass rate/pass^5 `1.000/1.000`; workflow có cost/success thấp nhất là `27.86`.
- Phân tích lỗi có chủ đích của swarm ở seed 55 và đề xuất chọn workflow làm shape chính.
- Điền báo cáo nhóm, decision record, research card và bảng đóng góp thành viên.

## Bằng chứng

Các lệnh đã chạy trong thư mục `src/`:

```powershell
python -m pytest -q
python -m pytest -q -m student -o addopts=
python -m lab8.crash_test --count 20 --out reports/crash.json
python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json
python -m lab8.check_submission
```

Kết quả xác nhận cuối cùng:

```text
303 passed
248 passed
crash_safety 20/20
0 FAIL, 1 WARN
```

Các file bằng chứng liên quan:

- `src/reports/benchmark.json`
- `src/reports/crash.json`
- `report/team/decision_adr.md`
- `report/team/research_card.md`
- `report/team/group_report.md`
- `TEAM.md`

## Công cụ hỗ trợ và tự kiểm tra

Có sử dụng Codex/ChatGPT để đọc tài liệu lab, giải thích checkpoint, phân tích output test và kiểm tra cấu trúc báo cáo. Kết quả cuối cùng được đối chiếu bằng các lệnh pytest, crash suite, benchmark và `check_submission` của repo; không tự bịa số liệu benchmark.

## Hạn chế

Phần đóng góp của tôi tập trung vào evaluation, integration và báo cáo; Git hiện chưa ghi nhận một commit shape riêng mang tên tôi. Các thông tin commit và test của các thành viên khác được lấy từ lịch sử Git của repo.
