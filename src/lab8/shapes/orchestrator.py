"""Shape C — orchestrator plus read-only investigators. Student work.

1. Build a handoff with `lab8.handoff.make_handoff`. Allowed tools are read-only.
   Never put parent_secret, raw headers, or the full claim row into facts.
2. `lab8.runtime.run_readonly_investigators` runs those tools.
3. The orchestrator quotes from the investigator's order view and calls
   `durability.issue_refund`. Investigators have no write registry.
   Pass the full quote; the host subtracts earlier refunds on the same order.
   `lookup_refund_history` is a read-only tool you may hand to an investigator.
4. Trace the sanitized handoff, not the parent context.

An LLM summary of the parent context is not a sanitizer. Use the allowlist.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.handoff import make_handoff
from lab8.runtime import run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import get_claim_view, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    # 1. Mở database. Budget đếm chi phí; Trace lưu nhật ký lần xử lý.
    conn = connect(store_path)
    budget = Budget()
    trace = Trace(make_run_id("orchestrator", claim_id, seed))

    def finish_run(
        status: str, proposal: int = 0, reason: str | None = None
    ) -> RunResult:
        """Ghi quyết định và trả kết quả dựa trên ledger thực tế."""
        trace.add("decision", {
            "status": status,
            "proposal_amount": proposal,
            "reason": reason,
        })
        return finish(
            conn,
            shape="orchestrator",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    try:
        # 2. Đọc claim qua tool, không lấy hoặc ghi toàn bộ row vào nhật ký.
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        if not claim.get("found"):
            return finish_run("failed", reason="unknown_claim")
        if not claim.get("order_id"):
            return finish_run("needs_info", reason="missing_order_id")

        # 3. Handoff là phiếu giao việc. Allowlist chỉ cấp các tool đọc.
        # Không chuyển ticket, secret, header hoặc lịch sử của parent.
        handoff = make_handoff(
            request_id=f"REQ-{claim_id}",
            claim_id=claim_id,
            task="check_applicable_policy",
            facts={},
            allowed_tools=[
                "lookup_order",
                "lookup_policy",
                "compute_compensation",
            ],
        )
        trace.add("handoff", handoff)

        # 4. Investigator tra đơn trước rồi tính tiền bằng tool Python.
        # principal_id giới hạn việc tra cứu theo chủ sở hữu đơn.
        investigated = run_readonly_investigators(
            conn, budget, handoff, principal_id=claim["principal_id"]
        )
        order_view = investigated["tools"].get("lookup_order", {})
        trace.add("order_check", {
            "visible": bool(order_view.get("visible")),
            "reason": order_view.get("reason"),
        })
        if not order_view.get("visible"):
            return finish_run("escalated", reason=order_view.get("reason"))

        # 5. Quote là mức quyền lợi tính từ đơn và policy hiện hành.
        # Không dùng số ngày trễ hoặc chỉ dẫn khách viết trong ticket.
        quote_payload = investigated["tools"]["compute_compensation"]
        proposal = int(quote_payload["amount_vnd"])
        trace.add("quote", quote_payload)
        if proposal <= 0:
            return finish_run("denied", reason=quote_payload.get("reason"))

        # 6. Chỉ orchestrator yêu cầu host ghi tiền; investigator không ghi.
        # Truyền quote ĐẦY ĐỦ: host kiểm approval, trừ tiền đã hoàn,
        # áp giới hạn và bảo đảm gọi lại không tạo thêm refund.
        outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
        if not outcome["ok"]:
            status = "failed" if outcome["conflict"] else "denied"
            return finish_run(status, proposal, outcome["reason"])
        return finish_run("resolved", proposal)

    except InjectedCrash:
        # Ghi nhật ký rồi ném lại lỗi để runner/test thấy crash thực sự.
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    finally:
        # Luôn đóng kết nối, kể cả khi trả kết quả sớm hoặc crash.
        conn.close()
