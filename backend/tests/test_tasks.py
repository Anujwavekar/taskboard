from datetime import date, timedelta

import pytest

TODAY = date.today()


def day(offset: int) -> str:
    return (TODAY + timedelta(days=offset)).isoformat()


def titles(client, headers, query=""):
    r = client.get(f"/api/tasks{query}", headers=headers)
    assert r.status_code == 200, r.text
    return [t["title"] for t in r.json()["tasks"]]


# ---------- create and validation ----------

def test_create_task_uses_defaults_and_trims_title(client, make_user):
    h, _ = make_user()
    r = client.post("/api/tasks", json={"title": "  Pay bill  "}, headers=h)
    assert r.status_code == 201
    task = r.json()
    assert task["title"] == "Pay bill"
    assert task["priority"] == "medium"
    assert task["is_completed"] is False
    assert task["description"] is None and task["due_date"] is None
    assert "user_id" not in task


@pytest.mark.parametrize("title", ["", "   "])
def test_empty_title_is_rejected(client, make_user, title):
    h, _ = make_user()
    r = client.post("/api/tasks", json={"title": title}, headers=h)
    assert r.status_code == 422
    assert r.json()["errors"]["title"] == "Title is required"


def test_other_invalid_fields_are_rejected(client, make_user):
    h, _ = make_user()
    assert client.post("/api/tasks", json={"title": "x" * 151}, headers=h).status_code == 422
    r = client.post("/api/tasks", json={"title": "ok", "priority": "urgent"}, headers=h)
    assert r.status_code == 422 and "priority" in r.json()["errors"]
    r = client.post("/api/tasks", json={"title": "ok", "due_date": "not-a-date"}, headers=h)
    assert r.status_code == 422 and "due_date" in r.json()["errors"]


def test_task_routes_require_a_token(client):
    assert client.get("/api/tasks").status_code == 401
    assert client.post("/api/tasks", json={"title": "x"}).status_code == 401


# ---------- update, complete, delete ----------

def test_toggle_complete_changes_only_that_field_and_counts(client, make_user, add_task):
    h, _ = make_user()
    task = add_task(h, title="Pay bill", priority="high", due_date=day(3))

    r = client.put(f"/api/tasks/{task['id']}", json={"is_completed": True}, headers=h)
    assert r.status_code == 200
    body = r.json()
    assert body["is_completed"] is True
    assert (body["title"], body["priority"], body["due_date"]) == ("Pay bill", "high", day(3))

    counts = client.get("/api/tasks", headers=h).json()["counts"]
    assert counts == {"total": 1, "pending": 0, "completed": 1}

    r = client.put(f"/api/tasks/{task['id']}", json={"is_completed": False}, headers=h)
    assert r.json()["is_completed"] is False


def test_edit_all_fields_and_clear_due_date(client, make_user, add_task):
    h, _ = make_user()
    task = add_task(h, title="Old", due_date=day(2))
    r = client.put(
        f"/api/tasks/{task['id']}",
        json={"title": "New", "description": "Details", "priority": "low", "due_date": None},
        headers=h,
    )
    body = r.json()
    assert (body["title"], body["description"], body["priority"], body["due_date"]) == (
        "New", "Details", "low", None,
    )


def test_update_rejects_null_or_empty_title(client, make_user, add_task):
    h, _ = make_user()
    task = add_task(h)
    assert client.put(f"/api/tasks/{task['id']}", json={"title": None}, headers=h).status_code == 422
    assert client.put(f"/api/tasks/{task['id']}", json={"title": "  "}, headers=h).status_code == 422


def test_delete_task(client, make_user, add_task):
    h, _ = make_user()
    task = add_task(h)
    assert client.delete(f"/api/tasks/{task['id']}", headers=h).status_code == 204
    assert titles(client, h) == []
    assert client.delete(f"/api/tasks/{task['id']}", headers=h).status_code == 404


# ---------- filter, search, sort ----------

def test_status_filter_and_counts_ignore_the_filter(client, make_user, add_task):
    h, _ = make_user()
    one = add_task(h, title="one")
    add_task(h, title="two")
    client.put(f"/api/tasks/{one['id']}", json={"is_completed": True}, headers=h)

    pending = client.get("/api/tasks?status=pending", headers=h).json()
    assert [t["title"] for t in pending["tasks"]] == ["two"]
    assert pending["counts"] == {"total": 2, "pending": 1, "completed": 1}

    assert titles(client, h, "?status=completed") == ["one"]
    assert sorted(titles(client, h, "?status=all")) == ["one", "two"]


def test_search_is_case_insensitive_and_matches_the_title_only(client, make_user, add_task):
    h, _ = make_user()
    add_task(h, title="Book dentist")
    add_task(h, title="Pay bill", description="dentist invoice")
    assert titles(client, h, "?search=DENT") == ["Book dentist"]


def test_search_treats_wildcards_literally(client, make_user, add_task):
    h, _ = make_user()
    add_task(h, title="100% done")
    add_task(h, title="a_b")
    add_task(h, title="axb")
    assert titles(client, h, "?search=%25") == ["100% done"]  # %25 is "%"
    assert titles(client, h, "?search=a_b") == ["a_b"]


def test_sort_by_due_date_puts_tasks_without_a_date_last(client, make_user, add_task):
    h, _ = make_user()
    add_task(h, title="later", due_date=day(5))
    add_task(h, title="none")
    add_task(h, title="sooner", due_date=day(1))
    assert titles(client, h, "?sort=due_date") == ["sooner", "later", "none"]


def test_sort_by_priority_high_then_medium_then_low(client, make_user, add_task):
    h, _ = make_user()
    add_task(h, title="low", priority="low")
    add_task(h, title="high", priority="high")
    add_task(h, title="medium", priority="medium")
    assert titles(client, h, "?sort=priority") == ["high", "medium", "low"]


def test_status_search_and_sort_work_together(client, make_user, add_task):
    h, _ = make_user()
    add_task(h, title="Pay bill", priority="medium")
    add_task(h, title="Book dentist", priority="low")
    done = add_task(h, title="Buy milk", priority="high")
    add_task(h, title="Walk", priority="high")
    client.put(f"/api/tasks/{done['id']}", json={"is_completed": True}, headers=h)

    result = titles(client, h, "?status=pending&search=b&sort=priority")
    assert result == ["Pay bill", "Book dentist"]


def test_invalid_filter_values_are_rejected(client, make_user):
    h, _ = make_user()
    assert client.get("/api/tasks?status=banana", headers=h).status_code == 422
    assert client.get("/api/tasks?sort=banana", headers=h).status_code == 422