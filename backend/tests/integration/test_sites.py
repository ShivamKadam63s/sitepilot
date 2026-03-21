from unittest.mock import patch


def test_list_sites_empty(client, auth_headers, seed_user):
    resp = client.get(
        f"/api/sites?tenant_id={seed_user.tenant_id}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["items"] == []


def test_create_site(client, auth_headers):
    with patch("app.services.git_service.GitService.init_repo", return_value="/tmp/test.git"):
        resp = client.post(
            "/api/sites",
            json={"name": "My Site", "slug": "my-site", "source_type": "upload"},
            headers=auth_headers,
        )
    assert resp.status_code == 201
    data = resp.json()
    assert data["slug"]   == "my-site"
    assert data["name"]   == "My Site"
    assert data["status"] == "draft"


def test_create_site_duplicate_slug(client, auth_headers):
    with patch("app.services.git_service.GitService.init_repo", return_value="/tmp/x.git"):
        client.post(
            "/api/sites",
            json={"name": "Site A", "slug": "dupe-slug", "source_type": "upload"},
            headers=auth_headers,
        )
        resp = client.post(
            "/api/sites",
            json={"name": "Site B", "slug": "dupe-slug", "source_type": "upload"},
            headers=auth_headers,
        )
    assert resp.status_code == 409


def test_create_site_invalid_slug(client, auth_headers):
    resp = client.post(
        "/api/sites",
        json={"name": "Bad", "slug": "UPPERCASE_SLUG", "source_type": "upload"},
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_get_site(client, auth_headers):
    with patch("app.services.git_service.GitService.init_repo", return_value="/tmp/g.git"):
        create = client.post(
            "/api/sites",
            json={"name": "Get Me", "slug": "get-me", "source_type": "upload"},
            headers=auth_headers,
        )
    site_id = create.json()["id"]
    resp    = client.get(f"/api/sites/{site_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == site_id


def test_delete_site(client, auth_headers):
    with patch("app.services.git_service.GitService.init_repo", return_value="/tmp/del.git"):
        create = client.post(
            "/api/sites",
            json={"name": "Delete Me", "slug": "delete-me", "source_type": "upload"},
            headers=auth_headers,
        )
    site_id = create.json()["id"]
    resp    = client.delete(f"/api/sites/{site_id}", headers=auth_headers)
    assert resp.status_code == 204

    # Confirm gone
    resp2 = client.get(f"/api/sites/{site_id}", headers=auth_headers)
    assert resp2.status_code == 404
