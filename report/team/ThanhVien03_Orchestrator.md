# Báo cáo cá nhân — Orchestrator và bảo mật

> File báo cáo riêng của thành viên 3. Điền thông tin cá nhân và đổi tên thành `MSSV_HoTen.md` trước khi nộp; giữ nguyên file mẫu của nhóm.

## 1. Thông tin thành viên

- Họ tên: [Tự điền]
- MSSV: [Tự điền]
- Email: [Tự điền]
- GitHub: [Tự điền]
- Vai trò: Thành viên 3 — Orchestrator và bảo mật.
- Commit triển khai: [Điền hash và liên kết sau khi commit phần việc thực tế]

## 2. Phần việc phụ trách

Phần việc phụ trách là shape C trong bài Lab 8 — From Workflows to Agents: triển khai bộ điều phối xử lý claim hoàn tiền của LogiX-VN tại `src/lab8/shapes/orchestrator.py`, sử dụng investigator chỉ đọc và kiểm soát dữ liệu chuyển qua handoff, trace.

Phạm vi gồm đọc claim, kiểm tra đầu vào, tạo phiếu giao việc theo allowlist, nhận kết quả điều tra, lấy quote từ tool tính bồi thường và yêu cầu host ghi refund. Phần triển khai sử dụng các module host có sẵn; không sửa `durability.py`, `policy.py`, `metrics.py`, config hoặc dữ liệu đầu vào.

Việc tích hợp workflow, single, chạy benchmark toàn nhóm và lựa chọn kiến trúc cuối cùng được phối hợp với các thành viên còn lại. Báo cáo này không khẳng định kết quả hidden hoặc kết quả benchmark chưa được đo.

## 3. Đóng góp cụ thể

### 3.1. Triển khai luồng điều phối

Giữ nguyên chữ ký `run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult` để tương thích với runner và bộ kiểm thử. Luồng xử lý gồm:

1. Mở kết nối SQLite, khởi tạo `Budget` để đếm chi phí và `Trace` để lưu nhật ký.
2. Đọc claim bằng `get_claim_view()`. Claim không tồn tại trả `failed`; thiếu `order_id` trả `needs_info`.
3. Tạo handoff bằng `make_handoff()` với `facts={}` và danh sách tool đọc: `lookup_order`, `lookup_policy`, `compute_compensation`.
4. Gọi `run_readonly_investigators()` với `principal_id` của claim. Nếu không tìm thấy đơn hoặc không được phép xem, trả `escalated`.
5. Lấy quote từ `compute_compensation`, dựa trên dữ liệu đơn và policy hiện hành. Quote bằng 0 trả `denied`, không gọi ghi refund.
6. Với quote dương, gọi `issue_refund()` để host kiểm approval, giới hạn tiền và chống ghi trùng. Host chấp nhận thì trả `resolved`; từ chối thì `denied`; xung đột số tiền thì `failed`.
7. Trả kết quả qua hàm phụ `finish_run()` và helper `finish()` để thông tin refund, audit khớp ledger thực tế.

### 3.2. Các quyết định về bảo mật

- Handoff chỉ chứa các trường được thư viện cho phép. Không chuyển toàn bộ claim, ticket, secret, header hoặc lịch sử ngữ cảnh cha.
- Investigator chỉ được cấp ba tool đọc nêu trên; không nhận `issue_refund` hoặc tool ghi audit.
- Dữ liệu đơn được tra cứu theo `principal_id`, tránh xử lý đơn của người khác.
- Ticket được coi là dữ liệu không đáng tin. Số ngày trễ trong ticket và chỉ dẫn như “bỏ qua policy” không quyết định số tiền hoặc quyền thực thi.
- Trace chỉ ghi handoff đã lọc, trạng thái kiểm quyền, quote và quyết định. Không ghi nguyên claim, đơn, nội dung ticket, số điện thoại, địa chỉ, tên hàng hoặc ghi chú nội bộ.
- `Trace` không tự làm sạch dữ liệu; việc chọn payload an toàn được thực hiện trước khi gọi `trace.add()`.

### 3.3. Tính đúng đắn của số tiền và độ bền

Quote là quyền lợi đầy đủ theo đơn và policy, khác với khoản thực tế được ghi sau khi áp giới hạn. Orchestrator truyền quote đầy đủ vào host, không tự trừ khoản đơn đã được hoàn trước đó. Ví dụ entitlement 150.000 VND và đơn đã nhận 30.000 VND thì host có thể chỉ ghi thêm 120.000 VND khi approval và các giới hạn khác cho phép.

`crash_at` được chuyển vào `issue_refund()`. Khi nhận `InjectedCrash`, chương trình ghi trace rồi ném lại lỗi bằng `raise`, không chuyển crash thành kết quả thành công. Khi chạy lại, cơ chế ledger và khóa `refund:{claim_id}` của host ngăn tạo thêm refund cho cùng claim. Khối `finally` đóng kết nối database ở cả nhánh trả kết quả sớm và nhánh crash.

### 3.4. Phạm vi kiểm thử và commit

- Đã sử dụng bộ test có sẵn để kiểm tra shape orchestrator và host.
- Chưa thêm hoặc sửa test mới trong phần triển khai được ghi nhận ở báo cáo này. Không nhận các test có sẵn là đóng góp tự viết.
- Commit cá nhân: [Tự bổ sung hash thực tế; không dùng commit starter làm minh chứng triển khai].
- `TEAM.md` yêu cầu mỗi thành viên có ít nhất một test đã thêm hoặc sửa. Đây là mục cần bổ sung trước khi chốt bài nộp nếu chưa hoàn thành.

## 4. Bằng chứng

Các lệnh bên dưới chạy trong thư mục `src/`, sử dụng Python của môi trường ảo trên Windows.

### 4.1. Kiểm thử tự động

| Phép kiểm | Lệnh | Kết quả đã xác nhận |
| --- | --- | --- |
| Riêng orchestrator | `.\.venv\Scripts\python.exe -m pytest -q -m student -o addopts= -k orchestrator` | 62 passed |
| Host dùng chung | `.\.venv\Scripts\python.exe -m pytest -q` | 54 passed |
| Crash suite có sẵn | `.\.venv\Scripts\python.exe -m lab8.crash_test --count 20 --out reports/crash.json` | File `src/reports/crash.json` ghi `count: 20`, `passed: 20`, `crash_safety: "20/20"` |

Các test student liên quan trong `src/tests/test_public_matrix.py`:

- `test_public_single_run_cases`: 12 claim một lần chạy × 5 seed = 60 test cho orchestrator.
- `test_t11_retry_keeps_one_refund`: chạy lại cùng claim, chỉ giữ một refund.
- `test_t12_crash_before_checkpoint_does_not_double_pay`: crash sau effect, trước checkpoint, sau đó resume không hoàn trùng.

Crash suite 20/20 kiểm tra host và kịch bản swarm tham chiếu theo công cụ có sẵn; không phải 20 phép thử trực tiếp cho orchestrator. Bằng chứng crash và retry riêng của orchestrator nằm ở hai test T11, T12 và các thao tác thử thủ công.

### 4.2. Chạy thủ công claim hợp lệ

```powershell
.\.venv\Scripts\python.exe -m lab8.run --shape orchestrator --claim-id C-001 --seed 11 --db data/orchestrator-retry.sqlite
```

Kết quả được ghi nhận trong phiên làm việc:

- Run id: `R-orchestrator-C-001-s11`.
- `status: resolved`, `proposal_amount: 35000`.
- Một refund có `amount_vnd: 35000`, khóa `refund:C-001`.
- `committed_audit_count: 1`.
- Trace: `src/traces/R-orchestrator-C-001-s11.json`.

### 4.3. Chạy thủ công claim có lời khai khác dữ liệu đơn

```powershell
.\.venv\Scripts\python.exe -m lab8.run --shape orchestrator --claim-id C-002 --seed 55 --db data/orchestrator-denied.sqlite
```

Kết quả được ghi nhận:

- Run id: `R-orchestrator-C-002-s55`.
- `status: denied`, `proposal_amount: 0`.
- `refund_effects: []`, `committed_audit_count: 0`.
- `error_reason: no_entitlement`.

Ticket khai trễ 5 ngày nhưng dữ liệu đơn ghi 2 ngày. Orchestrator giữ dữ liệu đơn làm căn cứ nên không tạo refund.

### 4.4. Giới hạn của kết quả

Hai lần chạy thủ công nêu trên đều ghi `model_calls: 0`, `tool_calls: 5`, `cost_estimate: 50.0`. Chi phí này là mô phỏng cho từng lần chạy, không phải số tiền hoàn hoặc hóa đơn API.

Bản hiện tại điều phối bằng code và runner investigator có sẵn, không gọi MockLLM; không mô tả nó là model tự lập kế hoạch. Kết quả public và host chưa chứng minh pass rate của bộ hidden, độ ổn định theo benchmark toàn bộ hoặc ưu thế so với ba kiến trúc còn lại.

Trace và SQLite là hiện vật cục bộ để kiểm tra, không commit theo quy định đề bài. Báo cáo crash do công cụ sinh, không sửa tay số liệu.

## 5. Công cụ AI đã dùng

Đã sử dụng ChatGPT/Codex để giải thích nghiệp vụ, làm rõ vai trò orchestrator–investigator–host, hỗ trợ viết trực tiếp code `orchestrator.py`, giải thích từng khối code, hướng dẫn lệnh PowerShell và soạn bản báo cáo này. Code có sự hỗ trợ trực tiếp của AI, không chỉ gợi ý ý tưởng.

Việc kiểm tra gồm chạy test orchestrator, test host và đối chiếu kết quả CLI của C-001, C-002. Các kết quả 62 passed, 54 passed được xác nhận qua thực thi trong phiên hỗ trợ; kết quả CLI thủ công do người thực hiện gửi để đối chiếu. Báo cáo crash 20/20 được kiểm tra từ file JSON đang có trong dự án.

Các tài liệu đối chiếu là `docs/business_rules.md`, `docs/contracts.md`, `RULES.md` và các module host có sẵn. Không dùng API key hoặc gọi model thật. Thông tin cá nhân, commit và phần tự đánh giá cuối cùng cần được người nộp kiểm tra, bổ sung trước khi nộp.

## 6. Tự đánh giá

Về sản phẩm kỹ thuật, phần orchestrator đã xử lý các nhánh nghiệp vụ được kiểm thử public, giữ giới hạn tool của investigator và sử dụng host để kiểm duyệt, ghi tiền. Bộ test riêng đạt 62/62 và test host đạt 54/54 tại thời điểm kiểm tra. Kết quả này phản ánh phạm vi kiểm thử hiện có, không thay thế benchmark và đánh giá hidden của cả nhóm.

Hạn chế của bản hiện tại là luồng điều phối được định nghĩa bằng code, chưa sử dụng MockLLM để lập kế hoạch hoặc soạn phản hồi. Phần test tự bổ sung và commit minh chứng cần hoàn thiện theo quy định bảng đóng góp.

- Mức độ tự giải thích được luồng xử lý và ranh giới bảo mật: [Tự đánh giá].
- Khó khăn thực tế và cách tự xử lý: [Tự bổ sung theo trải nghiệm cá nhân].
- Bài học rút ra: [Tự bổ sung sau khi đọc lại code, đặc biệt quote đầy đủ, allowlist và ledger khi retry].

### Các mục cần chốt trước khi nộp

- Điền thông tin cá nhân và đổi tên file đúng `MSSV_HoTen.md`.
- Bổ sung commit thực tế và test đã thêm hoặc sửa, cập nhật `TEAM.md`.
- Hoàn thiện phần tự đánh giá theo mức hiểu thực tế.
- Phối hợp người phụ trách tích hợp để cập nhật minh chứng nếu code hoặc kết quả kiểm thử thay đổi.
