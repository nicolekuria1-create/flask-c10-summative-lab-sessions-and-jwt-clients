from models import Note, User
from extensions import db


def signup(client, username="alice", password="password123"):
    return client.post(
        "/signup",
        json={"username": username, "password": password},
    )


def login(client, username="alice", password="password123"):
    return client.post(
        "/login",
        json={"username": username, "password": password},
    )


def test_signup_login_logout_and_check_session(client):
    res = signup(client)
    assert res.status_code == 201
    assert res.get_json()["username"] == "alice"

    res = client.get("/check_session")
    assert res.status_code == 200
    assert res.get_json()["username"] == "alice"

    res = client.delete("/logout")
    assert res.status_code == 204

    res = client.get("/check_session")
    assert res.status_code == 401

    res = login(client)
    assert res.status_code == 200
    assert res.get_json()["username"] == "alice"


def test_notes_are_protected_and_scoped_to_owner(client, app):
    res = client.get("/notes")
    assert res.status_code == 401

    signup(client, username="owner")
    create_res = client.post(
        "/notes",
        json={"title": "Owner Note", "content": "Private content", "mood": "focused"},
    )
    assert create_res.status_code == 201
    note_id = create_res.get_json()["id"]

    with app.app_context():
        other = User(username="other")
        other.set_password("password123")
        db.session.add(other)
        db.session.commit()

    client.delete("/logout")
    login(client, username="other", password="password123")

    res = client.get(f"/notes/{note_id}")
    assert res.status_code == 404

    res = client.patch(f"/notes/{note_id}", json={"title": "Hacked"})
    assert res.status_code == 404

    res = client.delete(f"/notes/{note_id}")
    assert res.status_code == 404


def test_notes_pagination_and_single_note_read(client):
    signup(client, username="pager")

    for idx in range(12):
        res = client.post(
            "/notes",
            json={"title": f"Note {idx}", "content": f"Content {idx}", "mood": "neutral"},
        )
        assert res.status_code == 201

    res = client.get("/notes?page=1&per_page=5")
    assert res.status_code == 200

    payload = res.get_json()
    assert payload["page"] == 1
    assert payload["per_page"] == 5
    assert payload["total"] == 12
    assert payload["pages"] == 3
    assert len(payload["items"]) == 5

    first_note_id = payload["items"][0]["id"]
    single = client.get(f"/notes/{first_note_id}")
    assert single.status_code == 200
    assert single.get_json()["id"] == first_note_id
