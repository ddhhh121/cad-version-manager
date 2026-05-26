import io


def _upload(client, pid, filename, content):
    return client.post(
        f"/api/projects/{pid}/upload",
        files={"file": (filename, io.BytesIO(content), "application/octet-stream")},
    )


def test_get_series_with_versions(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]
    _upload(client, pid, "a4齿轮.dxf", b"v1")
    _upload(client, pid, "a4齿轮.dxf", b"v2")

    # get series_id from upload result
    up = _upload(client, pid, "A3连杆.dxf", b"test")
    sid = up.json()["series_id"]

    resp = client.get(f"/api/series/{sid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["drawing_number"] == "A3连杆"
    assert data["version_count"] >= 1
    assert data["latest_version"] is not None


def test_list_versions(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]
    up = _upload(client, pid, "a4齿轮.dxf", b"v1")
    sid = up.json()["series_id"]

    resp = client.get(f"/api/series/{sid}/versions")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["version_number"] >= 1


def test_series_404(client):
    resp = client.get("/api/series/999")
    assert resp.status_code == 404
