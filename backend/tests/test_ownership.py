def test_other_user_sees_nothing(client, make_user, add_task):
    a, _ = make_user()
    b, _ = make_user()
    add_task(a, title="A's private task")
    body = client.get("/api/tasks", headers=b).json()
    assert body["tasks"] == []
    assert body["counts"] == {"total": 0, "pending": 0, "completed": 0}


def test_other_user_cannot_edit_complete_or_delete(client, make_user, add_task):
    a, _ = make_user()
    b, _ = make_user()
    task = add_task(a, title="A's private task")
    url = f"/api/tasks/{task['id']}"

    assert client.put(url, json={"title": "hacked"}, headers=b).status_code == 404
    assert client.put(url, json={"is_completed": True}, headers=b).status_code == 404
    assert client.delete(url, headers=b).status_code == 404

    mine = client.get("/api/tasks", headers=a).json()["tasks"]
    assert len(mine) == 1
    assert mine[0]["title"] == "A's private task"
    assert mine[0]["is_completed"] is False


def test_user_id_in_the_body_is_ignored(client, make_user):
    a, a_user = make_user()
    b, _ = make_user()
    r = client.post("/api/tasks", json={"title": "B's task", "user_id": a_user["id"]}, headers=b)
    assert r.status_code == 201
    assert [t["title"] for t in client.get("/api/tasks", headers=a).json()["tasks"]] == []
    assert [t["title"] for t in client.get("/api/tasks", headers=b).json()["tasks"]] == ["B's task"]


def test_malformed_task_id_returns_422(client, make_user):
    h, _ = make_user()
    assert client.put("/api/tasks/not-a-uuid", json={"title": "x"}, headers=h).status_code == 422