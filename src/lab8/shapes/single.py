"""Shape B — one bounded ReAct agent; refund writes stay in the host."""

from __future__ import annotations

import sqlite3
from typing import Any

from lab8.db import connect
from lab8.durability import InjectedCrash, issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, make_run_id
from lab8.shapes.common import finish
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
):
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(
    conn: sqlite3.Connection,
    claim_id: str,
    *,
    seed: int,
    crash_at: str | None,
):
    budget = Budget()
    trace = Trace(make_run_id("single", claim_id, seed))
    initial = {"claim": {"claim_id": claim_id}}

    def decide(observation: dict[str, Any]) -> dict[str, Any]:
        """Choose only read tools; the model never receives raw ticket contents."""
        previous_tool = observation.get("last_tool", "start")
        result = observation.get("last_result") or {}

        # MockLLM accounts for each ReAct decision. The controller uses verified
        # tool results for routing, never ticket instructions or model text for money.
        complete(
            budget,
            seed=seed,
            purpose="single_decide",
            prompt=f"step={budget.steps};previous_tool={previous_tool}",
        )

        if previous_tool == "start":
            action = {"tool": "get_claim_view", "args": {"claim_id": claim_id}}
        elif previous_tool == "get_claim_view":
            safe_claim = {
                key: result[key]
                for key in ("found", "claim_id", "order_id")
                if key in result
            }
            trace.add("claim_view", safe_claim)
            if not result.get("found"):
                return {"final": {"status": "failed", "proposal_amount": 0, "error_reason": "unknown_claim"}}
            if not result.get("order_id"):
                return {"final": {"status": "needs_info", "proposal_amount": 0, "error_reason": "missing_order_id"}}
            action = {
                "tool": "lookup_order",
                "args": {
                    "order_id": result["order_id"],
                    "principal_id": result["principal_id"],
                },
            }
        elif previous_tool == "lookup_order":
            if not result.get("visible"):
                trace.add("order_lookup", {"visible": False, "reason": result.get("reason")})
                return {
                    "final": {
                        "status": "escalated",
                        "proposal_amount": 0,
                        "error_reason": result.get("reason"),
                    }
                }
            order = result["order"]
            trace.add(
                "order_lookup",
                {
                    "visible": True,
                    "order": {
                        key: order[key]
                        for key in (
                            "order_id",
                            "status",
                            "delay_days",
                            "shipping_fee_vnd",
                            "paid_vnd",
                            "damage_verified",
                            "carrier",
                        )
                        if key in order
                    },
                },
            )
            action = {"tool": "compute_compensation", "args": {"order": order}}
        elif previous_tool == "compute_compensation":
            amount = int(result.get("amount_vnd", 0))
            quote = {
                "amount_vnd": amount,
                "reason": result.get("reason"),
                "clause_ids": result.get("clause_ids", []),
                "parts": result.get("parts", {}),
            }
            trace.add("quote", quote)
            return {
                "final": {
                    "status": "resolved" if amount > 0 else "denied",
                    "proposal_amount": amount,
                    "error_reason": None if amount > 0 else result.get("reason"),
                }
            }
        else:
            return {"final": {"status": "failed", "proposal_amount": 0, "error_reason": "unexpected_react_state"}}

        trace.add("agent_action", {"tool": action["tool"]})
        return action

    try:
        run = run_react(
            conn,
            budget,
            observation=initial,
            decide=decide,
            max_steps=8,
        )
        final = run["final"]
        status = final.get("status", "failed")
        proposal = int(final.get("proposal_amount", 0))
        error_reason = final.get("error_reason")

        if run["stopped"] == "step_cap":
            status = "failed"
            proposal = 0
            error_reason = "step_cap"

        if status == "resolved" and proposal > 0:
            try:
                outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
            except InjectedCrash:
                trace.add("crash", {"at": crash_at})
                trace.write()
                raise

            if not outcome["ok"]:
                status = "failed" if outcome["conflict"] else "denied"
                error_reason = outcome["reason"]
            trace.add(
                "refund_gate",
                {"ok": bool(outcome["ok"]), "reason": outcome["reason"], "conflict": bool(outcome["conflict"])},
            )

        trace.add("decision", {"status": status, "proposal_amount": proposal})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=error_reason,
        )
    except Exception as exc:
        # Preserve injected crashes for the durability suite; turn other runtime
        # errors into a contract-shaped result while keeping trace content safe.
        if isinstance(exc, InjectedCrash):
            raise
        trace.add("error", {"reason": type(exc).__name__})
        return finish(
            conn,
            shape="single",
            claim_id=claim_id,
            seed=seed,
            status="failed",
            proposal_amount=0,
            budget=budget,
            trace=trace,
            error_reason=type(exc).__name__,
        )
