from driftshell.memory.store import get_recent, save
from driftshell.models.schemas import CommandRecord, GateDecision


def _make_record(query: str, cmd: str) -> CommandRecord:
    return CommandRecord(
        nl_query=query,
        shell_command=cmd,
        risk_score=2,
        gate_decision=GateDecision.AUTO_EXEC,
        exit_code=0,
    )


def test_save_and_retrieve():
    save(_make_record("list files", "ls -la"))
    records = get_recent(10)
    assert len(records) == 1
    assert records[0].nl_query == "list files"
    assert records[0].shell_command == "ls -la"


def test_get_recent_limit():
    for i in range(5):
        save(_make_record(f"query {i}", f"cmd_{i}"))
    records = get_recent(3)
    assert len(records) == 3


def test_get_recent_order():
    save(_make_record("first", "cmd1"))
    save(_make_record("second", "cmd2"))
    records = get_recent(10)
    assert records[0].nl_query == "first"
    assert records[1].nl_query == "second"
