"""Testes de aplicação: inicialização, /health e OpenAPI (sem banco)."""


def test_app_initializes_and_serves_openapi(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    assert spec["info"]["title"] == "Blue API"


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_unknown_route_returns_404(client):
    response = client.get("/rota-inexistente")
    assert response.status_code == 404


def test_openapi_exposes_auth_paths(client):
    spec = client.get("/openapi.json").json()
    paths = spec["paths"]
    assert "/auth/register" in paths
    assert "/auth/login" in paths
    assert "/auth/me" in paths
