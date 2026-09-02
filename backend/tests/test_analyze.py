from tests.conftest import make_png_bytes


async def test_analyze_valid_image_returns_probability(client, png_bytes):
    resp = await client.post(
        "/v1/analyze", files={"file": ("test.png", png_bytes, "image/png")}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert 0.0 <= body["prob_ai"] <= 1.0
    assert body["label"] in {"ai-generated", "real"}
    assert round(body["prob_ai"] + body["prob_real"], 4) == 1.0


async def test_analyze_is_deterministic_for_same_image(client, png_bytes):
    r1 = await client.post("/v1/analyze", files={"file": ("a.png", png_bytes, "image/png")})
    r2 = await client.post("/v1/analyze", files={"file": ("b.png", png_bytes, "image/png")})
    assert r1.json()["prob_ai"] == r2.json()["prob_ai"]


async def test_analyze_rejects_unsupported_content_type(client):
    resp = await client.post(
        "/v1/analyze", files={"file": ("test.gif", b"GIF89a", "image/gif")}
    )
    assert resp.status_code == 415


async def test_analyze_rejects_oversized_file(client, monkeypatch):
    from app.utils import image_validation

    # `settings` é lido uma vez no import do módulo (padrão do projeto: env é
    # fixo por processo) — para o teste, faz patch direto no objeto já
    # carregado em vez de tentar recarregar a configuração em runtime.
    monkeypatch.setattr(image_validation.settings, "MAX_UPLOAD_MB", 0)

    big = make_png_bytes(size=(64, 64))
    resp = await client.post("/v1/analyze", files={"file": ("big.png", big, "image/png")})
    assert resp.status_code == 413


async def test_analyze_rejects_corrupted_image_with_valid_content_type(client):
    garbage = b"not a real image but claims to be one" * 10
    resp = await client.post(
        "/v1/analyze", files={"file": ("fake.png", garbage, "image/png")}
    )
    assert resp.status_code == 422


async def test_analyze_rejects_empty_file(client):
    resp = await client.post("/v1/analyze", files={"file": ("empty.png", b"", "image/png")})
    assert resp.status_code == 422
