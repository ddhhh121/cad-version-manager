import io


def _upload(client, pid, filename, content):
    return client.post(
        f"/api/projects/{pid}/upload",
        files={"file": (filename, io.BytesIO(content), "application/octet-stream")},
    )


def test_get_version(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]
    up = _upload(client, pid, "a4齿轮.dxf", b"test content")
    vid = up.json()["version_id"]

    resp = client.get(f"/api/versions/{vid}")
    assert resp.status_code == 200
    assert resp.json()["filename"] == "a4齿轮.dxf"


def test_update_change_note(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]
    up = _upload(client, pid, "a4齿轮.dxf", b"test")
    sid = up.json()["series_id"]
    vid = up.json()["version_id"]

    resp = client.post(
        f"/api/series/{sid}/versions/{vid}/note",
        json={"change_note": "改了齿数"},
    )
    assert resp.status_code == 200

    resp = client.get(f"/api/versions/{vid}")
    assert resp.json()["change_note"] == "改了齿数"


def test_compare_versions(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]

    # Upload two versions of the same drawing
    v1 = _upload(client, pid, "A3动刀刃.dxf", b"v1 content")
    v2 = _upload(client, pid, "A3动刀刃.dxf", b"v2 content different")

    vid1 = v1.json()["version_id"]
    vid2 = v2.json()["version_id"]

    resp = client.get(f"/api/compare/{vid1}/{vid2}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["hash_match"] is False
    assert len(data["diffs"]) >= 2
    sha_diff = [d for d in data["diffs"] if d["field"] == "file_hash"][0]
    assert sha_diff["changed"] is True


def test_compare_cross_series_rejected(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]
    v1 = _upload(client, pid, "A3动刀刃.dxf", b"a")
    v2 = _upload(client, pid, "a4齿轮.dxf", b"b")

    resp = client.get(
        f"/api/compare/{v1.json()['version_id']}/{v2.json()['version_id']}"
    )
    assert resp.status_code == 400
