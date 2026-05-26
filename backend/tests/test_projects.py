def test_create_project(client):
    resp = client.post("/api/projects", json={"name": "测试项目", "description": "测试"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "测试项目"
    assert data["series_count"] == 0
    assert "id" in data


def test_list_projects(client):
    client.post("/api/projects", json={"name": "项目A"})
    client.post("/api/projects", json={"name": "项目B"})
    resp = client.get("/api/projects")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["name"] == "项目B"  # 最新在前


def test_get_project(client):
    resp = client.post("/api/projects", json={"name": "测试"})
    pid = resp.json()["id"]
    resp = client.get(f"/api/projects/{pid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "测试"
    assert "series_list" in data
    assert data["series_list"] == []


def test_get_project_404(client):
    resp = client.get("/api/projects/999")
    assert resp.status_code == 404
