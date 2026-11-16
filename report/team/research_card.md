# Research card

File này nằm cố định ở `report/team/research_card.md`; `python -m lab8.check_submission` đọc cột "Nhóm điền" bằng máy.

Phần này nối tiếp phần mini research ở buổi lý thuyết (slide 62–63). Chọn **một** câu R1–R4, điền 6 dòng, rồi biến nó thành **một ablation** chạy được trong lab: giữ nguyên model (MockLLM), tool, seed, corpus và giá, chỉ thay đổi một biến.

| Câu | Nguồn (thư viện tham khảo, slide 68–69) | Câu hỏi gợi ý cho lab |
| --- | --- | --- |
| R1 · Scaling | Google Research 2026, *Towards a Science of Scaling Agent Systems* | Task claims chủ yếu tuần tự hay song song được? Dự đoán thêm investigator sẽ làm pass rate và cost/success thay đổi thế nào. |
| R2 · Failure taxonomy | MAST, NeurIPS 2025, *Why Do Multi-Agent LLM Systems Fail?* | Các trial fail của swarm (seed 55) thuộc nhóm nào: lỗi giao việc, lệch mục tiêu, hay lỗi kiểm chứng? |
| R3 · Architecture choices | AgentArch, AACL 2026 | Nếu đổi topology mà giữ nguyên mọi thứ khác, biến nào phải cố định để kết luận còn đúng? |
| R4 · Evaluation confounders | EMNLP 2026, *Rethinking Evaluation of MAS Efficiency* | Làm sao chứng minh chênh lệch giữa A/B/C/D là do topology, không phải do prompt, tool hay seed? |

## Phiếu của nhóm

Điền vào cột cuối. Không xóa hai cột đầu.

| Field | Hướng dẫn | Nhóm điền |
| --- | --- | --- |
| CÂU | R1 / R2 / R3 / R4 | R3 |
| SOURCE | Paper/blog, năm, URL, loại bằng chứng (benchmark, production report, blog kinh nghiệm) | AgentArch, AACL 2026, tài liệu lý thuyết của lab; bằng chứng benchmark so sánh kiến trúc |
| CLAIM | Một kết luận gốc của nguồn. Không viết rộng hơn phạm vi paper | Thay đổi topology có thể làm thay đổi hiệu năng và chi phí, nên phải so sánh trong cùng điều kiện thay vì mặc định multi-agent tốt hơn. |
| BOUNDARY | Model / dataset / setup giới hạn kết luận đó | Kết quả của nguồn phụ thuộc model, tool, dataset, prompt, evaluator và topology; lab này dùng MockLLM seeded, dữ liệu synthetic và không đo latency thật. |
| HYPOTHESIS | Nếu đổi shape A→B (hoặc bật/tắt một thành phần), metric X sẽ đổi theo hướng nào, khoảng bao nhiêu | Workflow sẽ giữ pass rate tương đương các shape đúng nhưng có cost/success và số bước thấp hơn; single/orchestrator sẽ tốn hơn do thêm model/investigator calls. |
| METHOD | Biến giữ cố định: model, tools, seed, corpus, giá, evaluator. Biến duy nhất được thay đổi: … | Giữ cố định MockLLM, tools, seeds 11/22/33/44/55, public claims, world state, pricing và evaluator; chỉ thay shape workflow/single/orchestrator/swarm. |
| FAILURE / METRIC | Một lỗi dự kiến và cách đo nó: pass rate, pass^5, variance, cost/success, leak, bypass | Dự kiến swarm có variance hoặc fail ở seed 55; đo pass rate, pass^5, seed variance, cost/success, steps, crash safety, secret leak và approval bypass. |

## Kết quả ablation

- Lệnh đã chạy (copy nguyên văn): `python -m lab8.benchmark --shapes workflow,single,orchestrator,swarm --cases data/public_claims.jsonl --seeds 11,22,33,44,55 --out reports/benchmark.json`
- Run id / file report: `R-workflow-C-001-s11`; `src/reports/benchmark.json`
- Kết quả so với hypothesis (đúng / sai / không kết luận được), kèm số liệu: Đúng trên bộ public. Workflow, single và orchestrator đều đạt pass rate/pass^5 = 1.000/1.000; cost/success lần lượt là 27.86, 30.27 và 46.43. Swarm đạt 0.986/0.929, variance 0.000816 và cost/success 49.57. Kết quả ủng hộ việc chọn workflow trong setup này.
- Giới hạn: MockLLM không phải model sản xuất, latency là `unavailable`.

Muốn đi xa hơn một ablation để lấy điểm cộng thì xem [docs/bonus_topics.md](../../docs/bonus_topics.md).
