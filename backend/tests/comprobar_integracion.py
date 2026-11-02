"""Comprobación real del proxy Nginx desde la red de Docker Compose."""
import json
import urllib.request
import urllib.error

BASE = "http://frontend"

def request(path, data=None):
    body = None if data is None else json.dumps(data).encode()
    req = urllib.request.Request(BASE + path, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.status, response.read()

if __name__ == "__main__":
    status, page = request("/")
    assert status == 200 and b"Clasificador de tumores" in page
    status, raw = request("/api/health")
    assert status == 200 and json.loads(raw)["model_loaded"] is True
    status, raw = request("/api/model-info")
    meta = json.loads(raw)
    assert status == 200 and len(meta["feature_names"]) == 30
    sample = [19.55,28.77,133.6,1207.0,0.0926,0.2063,0.1784,0.1144,0.1893,0.06232,0.8426,1.199,7.158,106.4,0.006356,0.04765,0.03863,0.01519,0.01936,0.005252,25.05,36.27,178.6,1926.0,0.1281,0.5329,0.4251,0.1941,0.2818,0.1005]
    status, raw = request("/api/predict", {"features": sample})
    result = json.loads(raw)
    assert status == 200 and result["diagnosis"] in ("maligno", "benigno")
    assert result["model_version"] == meta["version"]
    assert abs(result["probability_benign"] + result["probability_malignant"] - 1) < 1e-5
    try:
        request("/api/predict", {"features": [1, 2]})
    except urllib.error.HTTPError as error:
        assert error.code == 422
    else:
        raise AssertionError("La API no rechazo una entrada invalida")
    print("OK: web, proxy Nginx, salud, metadatos, prediccion y rechazo 422.")
    print(json.dumps(result, indent=2))
