"""Shape A — deterministic workflow. Student work.

Signature (do not change):

    run_claim(claim_id, *, seed, store_path, crash_at=None) -> RunResult

Suggested steps. Money stays in code (`lab8.tools.compute_compensation`).

1. Open the store. Read the claim through `get_claim_view` (not SELECT *).
2. Missing order_id -> status `needs_info`. Do not write the ledger.
3. `lookup_order`. If not visible -> `escalated`. Do not copy phone, address, item, internal note.
4. Quote from the order row. Ignore delay numbers written in the ticket.
5. Quote amount 0 -> `denied`. Do not call issue_refund.
6. Quote amount > 0 -> `durability.issue_refund(conn, claim_id, <full quote>)`.
   Pass the FULL quote. The host checks the claim's own approval and subtracts
   what earlier claims already got for the same order (T13, T14). Do not
   subtract it yourself or the host subtracts twice.
   Auth failure or order already refunded -> `denied` (the host writes `policy_denied`).
   `proposal_amount` stays the full quote. Amount conflict -> `failed`.
7. Success -> `resolved`. One ledger row, one `refund_committed` audit.
8. Use MockLLM only to draft the reply text, if you want a model call at all.

The model must not choose the refund amount and must not commit the refund.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    run_id = make_run_id("workflow", claim_id, seed)
    trace = Trace(run_id)

    # 1. Đọc claim an toàn qua get_claim_view (không dùng SELECT * để tránh lộ secret)
    budget.add_tool(tool_cost())
    claim_view = get_claim_view(conn, claim_id)
    if not claim_view.get("found"):
        trace.add("error", {"reason": "unknown_claim"})
        return finish(
            conn,
            shape="workflow",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="unknown_claim",
        )

    # 2. Kiểm tra order_id
    order_id = claim_view.get("order_id")
    if not order_id:
        trace.add("decision", {"status": "needs_info"})
        return finish(
            conn,
            shape="workflow",
            claim_id=claim_id,
            seed=seed,
            status="needs_info",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason="missing_order_id",
        )

    # 3. lookup_order (kiểm tra quyền sở hữu và sự tồn tại của đơn hàng)
    budget.add_tool(tool_cost())
    order_view = lookup_order(conn, order_id, claim_view["principal_id"])
    trace.add("order_lookup", {"visible": order_view.get("visible"), "reason": order_view.get("reason")})
    if not order_view.get("visible"):
        return finish(
            conn,
            shape="workflow",
            claim_id=claim_id,
            seed=seed,
            status="escalated",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=order_view.get("reason", "order_not_visible"),
        )

    # 4. Tính toán bồi thường bằng code qua compute_compensation
    budget.add_tool(tool_cost())
    compensation = compute_compensation(conn, order_view["order"])
    quote_amount = int(compensation.get("amount_vnd", 0))
    trace.add("quote", {"amount_vnd": quote_amount, "reason": compensation.get("reason")})

    # 5. Nếu quote amount == 0 -> denied (không gọi issue_refund)
    if quote_amount == 0:
        return finish(
            conn,
            shape="workflow",
            claim_id=claim_id,
            seed=seed,
            status="denied",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=compensation.get("reason", "not_entitled"),
        )

    # 6. Nếu quote amount > 0 -> gọi host qua issue_refund
    # Truyền crash_at vào và KHÔNG bắt InjectedCrash (để test crash bắt được)
    # Truyền full quote_amount, host sẽ tự trừ phần đã refund trước đó nếu có
    refund_res = issue_refund(conn, claim_id, quote_amount, crash_at=crash_at)
    trace.add("issue_refund", {"ok": refund_res.get("ok"), "reason": refund_res.get("reason")})

    if refund_res.get("ok"):
        return finish(
            conn,
            shape="workflow",
            claim_id=claim_id,
            seed=seed,
            status="resolved",
            proposal_amount=quote_amount,
            budget=budget,
            trace=trace,
        )

    if refund_res.get("conflict"):
        return finish(
            conn,
            shape="workflow",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=quote_amount,
            budget=budget,
            trace=trace,
            error_reason="amount_conflict",
        )

    # Từ chối duyệt (approval không hợp lệ, không khớp claim, hoặc đơn đã hoàn đủ)
    return finish(
        conn,
        shape="workflow",
        claim_id=claim_id,
        seed=seed,
        status="denied",
        proposal_amount=quote_amount,
        budget=budget,
        trace=trace,
        error_reason=refund_res.get("reason", "policy_denied"),
    )
