import io


def test_upload_new_dxf_creates_series_and_version(client):
    # 先创建项目
    resp = client.post("/api/projects", json={"name": "测试项目"})
    pid = resp.json()["id"]

    content = b"0\nSECTION\n2\nENTITIES\n0\nENDSEC\n0\nEOF\n"
    resp = client.post(
        f"/api/projects/{pid}/upload",
        files={"file": ("A3动刀刃.dxf", io.BytesIO(content), "application/octet-stream")},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["drawing_number"] == "A3动刀刃"
    assert data["version_number"] == 1
    assert data["is_new_series"] is True
    assert "series_id" in data


def test_upload_duplicate_hash_rejected(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]

    content = b"test dwg content"
    client.post(
        f"/api/projects/{pid}/upload",
        files={"file": ("a4齿轮.dxf", io.BytesIO(content), "application/octet-stream")},
    )
    # 相同内容上传到相同图号（使用相同文件名）应被拒绝
    resp = client.post(
        f"/api/projects/{pid}/upload",
        files={"file": ("a4齿轮.dxf", io.BytesIO(content), "application/octet-stream")},
    )
    assert resp.status_code == 409


def test_upload_same_series_increments_version(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]

    resp1 = client.post(
        f"/api/projects/{pid}/upload",
        files={"file": ("A3动刀刃.dxf", io.BytesIO(b"v1 content"), "application/octet-stream")},
    )
    assert resp1.json()["version_number"] == 1

    resp2 = client.post(
        f"/api/projects/{pid}/upload",
        files={"file": ("A3动刀刃_副本.dxf", io.BytesIO(b"v2 content"), "application/octet-stream")},
    )
    assert resp2.json()["version_number"] == 2
    assert resp2.json()["is_new_series"] is False
    assert resp2.json()["series_id"] == resp1.json()["series_id"]


def test_upload_reject_non_dwg_dxf(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]

    resp = client.post(
        f"/api/projects/{pid}/upload",
        files={"file": ("readme.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert resp.status_code == 400


def test_upload_project_404(client):
    resp = client.post(
        "/api/projects/999/upload",
        files={"file": ("test.dxf", io.BytesIO(b"x"), "application/octet-stream")},
    )
    assert resp.status_code == 404
