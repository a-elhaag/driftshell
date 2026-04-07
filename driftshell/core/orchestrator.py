from __future__ import annotations

from dataclasses import dataclass

from driftshell.core import executor, explainer, hardware, limiter, nlu
from driftshell.db import audit
from driftshell.memory import store
from driftshell.models.schemas import CommandRecord, ExecutionResult, GateDecision, RiskResult
from driftshell.safety import blocklist, gate, scorer
from driftshell.snapshots import capture
from driftshell.config.loader import get_config


@dataclass
class OrchestratorResult:
    command: str
    risk: RiskResult | None
    decision: GateDecision | None
    execution: ExecutionResult | None
    explanation: str | None


def run(query: str, explain_mode: bool = False, dry_run: bool = False) -> OrchestratorResult:
    cfg = get_config()

    # Step 1: enforce daily command limit
    limiter.check_command_limit()

    profile = hardware.get_hardware_profile()
    model = profile.selected_model

    # Step 2: generate shell command from NL
    command = nlu.generate_command(query, model)

    # Step 3: blocklist check
    try:
        blocklist.check(command)
    except blocklist.BlockedCommandError as e:
        audit.log_event("blocked", f"{command!r} matched {e.pattern!r}")
        return OrchestratorResult(
            command=command,
            risk=None,
            decision=GateDecision.BLOCKED,
            execution=None,
            explanation=None,
        )

    # Step 4: risk scoring (unless skipped)
    if cfg.skip_scoring:
        risk = RiskResult(score=3, raw_response="scoring_skipped")
    else:
        risk = scorer.score(command, model)

    # Step 5: explain mode — show command + explanation, no execution
    if explain_mode:
        explanation = explainer.explain(command, model)
        audit.log_event("explained", command)
        return OrchestratorResult(
            command=command,
            risk=risk,
            decision=None,
            execution=None,
            explanation=explanation,
        )

    # Step 6: gate decision
    decision = gate.evaluate(command, risk)

    if decision == GateDecision.ABORTED:
        audit.log_event("aborted", command)
        record = CommandRecord(
            nl_query=query,
            shell_command=command,
            risk_score=risk.score,
            gate_decision=GateDecision.ABORTED,
        )
        store.save(record)
        limiter.increment_command()
        return OrchestratorResult(command=command, risk=risk, decision=decision, execution=None, explanation=None)

    if dry_run:
        audit.log_event("dry_run", command)
        return OrchestratorResult(command=command, risk=risk, decision=decision, execution=None, explanation=None)

    # Step 7: check exec limit for auto-exec
    if decision == GateDecision.AUTO_EXEC:
        limiter.check_exec_limit()

    # Step 8: snapshot before execution
    record = CommandRecord(
        nl_query=query,
        shell_command=command,
        risk_score=risk.score,
        gate_decision=decision,
    )
    command_id = store.save(record)
    capture.capture(command, command_id=command_id)

    # Step 9: execute
    result = executor.run(command)

    # Step 10: update record with outcome
    conn_record = CommandRecord(
        nl_query=query,
        shell_command=command,
        risk_score=risk.score,
        gate_decision=decision,
        exit_code=result.exit_code,
        stdout=result.stdout,
        stderr=result.stderr,
    )
    # Update the already-saved row
    from driftshell.db import get_connection
    get_connection().execute(
        "UPDATE commands SET exit_code=?, stdout=?, stderr=? WHERE id=?",
        (result.exit_code, result.stdout, result.stderr, command_id),
    )

    limiter.increment_command()
    if decision == GateDecision.AUTO_EXEC:
        limiter.increment_exec()

    audit.log_event(
        "executed" if result.exit_code == 0 else "failed",
        f"exit={result.exit_code} cmd={command!r}",
    )

    return OrchestratorResult(
        command=command,
        risk=risk,
        decision=decision,
        execution=result,
        explanation=None,
    )
