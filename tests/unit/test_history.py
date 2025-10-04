import time

from src.history import DEFAULT_HISTORY_LIMIT, update_local_history


def make_entry(idx: int, etype: str = "ai"):
    return {
        "type": etype,
        "question": f"q{idx}" if etype == "ai" else None,
        "sql": f"SELECT {idx};",
        "provider": "claude" if etype == "ai" else "manual",
        "time": 0.01 * idx,
        "ts": time.time() + idx,
    }


def test_update_local_history_creates_new_list():
    updated = update_local_history(None, entry=make_entry(1))
    assert len(updated) == 1
    assert updated[0]["sql"] == "SELECT 1;"


def test_prepends_and_trims():
    history = []
    for i in range(5):
        history = update_local_history(history, entry=make_entry(i))
    assert len(history) == 5
    # newest first
    assert history[0]["sql"] == "SELECT 4;"
    assert history[-1]["sql"] == "SELECT 0;"
    # exceed limit
    for i in range(5, 22):  # push beyond default limit (15)
        history = update_local_history(history, entry=make_entry(i))
    assert len(history) == DEFAULT_HISTORY_LIMIT
    # newest still first
    assert history[0]["sql"] == "SELECT 21;"


def test_manual_and_ai_distinction():
    history = []
    history = update_local_history(history, entry=make_entry(1, etype="ai"))
    history = update_local_history(history, entry=make_entry(2, etype="manual"))
    assert history[0]["type"] == "manual"
    assert history[1]["type"] == "ai"


def test_custom_limit():
    history = []
    for i in range(10):
        history = update_local_history(history, entry=make_entry(i), limit=3)
    assert len(history) == 3
    # Should contain last three entries inserted (9,8,7) in that order
    assert [e["sql"] for e in history] == ["SELECT 9;", "SELECT 8;", "SELECT 7;"]
