# Decision record

Điền sau dấu `:` trên cùng dòng, không xóa nhãn. Giảng viên và `python -m lab8.check_submission` (chạy trong `src/`) đọc các dòng này bằng máy. Không đổi tên hay dời file này khỏi `report/team/`.
`Shape chọn` phải là đúng một trong: `workflow`, `single`, `orchestrator`, `swarm`. Đây là shape được chấm cổng hidden.

- Shape chọn: workflow
- Commit hash: 0b86ca5
- Run id dẫn chứng: R-workflow-C-001-s11 (reports/benchmark.json)
- Pass rate / pass^5 / seed min-max / variance: 1.000 / 1.000 / 1.000-1.000 / 0.000000
- Cost per success (mô phỏng, VND): 27.86
- Crash safety: 20/20 (src/reports/crash.json)
- Secret leak / approval bypass: 0 / 0

Ví dụ một dòng đã điền: `- Shape chọn: workflow`, `- Crash safety: 20/20 (src/reports/crash.json)`.

## Vì sao shape này

Nhóm chọn workflow vì workflow đạt pass rate 1.000 và pass^5 1.000 trên cùng bộ public, cùng các seed 11, 22, 33, 44, 55, trong khi có cost per success thấp nhất là 27.86 VND mô phỏng và số bước trung bình thấp nhất là 2.50. Kết quả cũng ổn định với variance bằng 0.000000. Single và orchestrator cũng đạt 1.000 nhưng tốn lần lượt 30.27 và 46.43 VND mô phỏng, nên chưa cho thấy lợi ích đủ lớn để đổi lấy chi phí và độ phức tạp cao hơn.

## Có đáng đổi lấy multi-agent không

Trên benchmark này, multi-agent không cải thiện pass rate so với workflow: single và orchestrator đều 1.000, còn swarm thấp hơn ở 0.986 và pass^5 0.929. Vì vậy nhóm giữ workflow. Quyết định có thể đảo nếu hidden hoặc dữ liệu thực tế cho thấy agent đạt độ bao phủ cao hơn đáng kể trên các claim mơ hồ, hoặc nếu task có nhiều phần độc lập cần điều tra song song; khi đó mức tăng pass rate phải bù được cost, số bước và rủi ro variance.

## Trace và bằng chứng

Trace ghi run id, các bước đọc dữ liệu đã allowlist, quyết định nghiệp vụ, proposal amount, lời gọi host và các audit cần thiết. Nhóm cố ý không ghi parent secret, header, số điện thoại, địa chỉ, tên hàng, internal note, full claim row hoặc full order row để trace vừa đủ cho grader nhưng không trở thành nơi rò rỉ dữ liệu. Trace của mỗi lần chạy được ghi trong thư mục mà scanner kiểm tra và có run id khớp với RunResult.

## Giới hạn

MockLLM không phải model sản xuất và latency là `unavailable`; cost chỉ là chi phí mô phỏng. Benchmark public nhỏ hơn hidden và không chứng minh chất lượng triển khai thực tế. Số liệu được lấy từ reports/benchmark.json và reports/crash.json, không sửa tay để đạt ngưỡng.
