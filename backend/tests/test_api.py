from fastapi.testclient import TestClient
from app.main import app

SAMPLE = [19.55, 28.77, 133.6, 1207.0, 0.0926, 0.2063, 0.1784, 0.1144, 0.1893, 0.06232, 0.8426, 1.199, 7.158, 106.4, 0.006356, 0.04765, 0.03863, 0.01519, 0.01936, 0.005252, 25.05, 36.27, 178.6, 1926.0, 0.1281, 0.5329, 0.4251, 0.1941, 0.2818, 0.1005]

def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["model_loaded"] is True

def test_root_and_model_info():
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        response = client.get("/model-info")
        assert response.status_code == 200
        assert len(response.json()["feature_names"]) == 30

def test_valid_prediction():
    with TestClient(app) as client:
        response = client.post("/predict", json={"features": SAMPLE})
        assert response.status_code == 200
        body = response.json()
        assert body["diagnosis"] in ("maligno", "benigno")
        assert 0 <= body["probability_benign"] <= 1
        assert 0 <= body["probability_malignant"] <= 1
        assert abs(body["probability_benign"] + body["probability_malignant"] - 1) < 1e-5

def test_missing_features():
    with TestClient(app) as client:
        response = client.post("/predict", json={"features": [1.0, 2.0]})
        assert response.status_code == 422

def test_non_numeric_value():
    with TestClient(app) as client:
        response = client.post("/predict", json={"features": ["x"] * 30})
        assert response.status_code == 422

def test_extra_features():
    with TestClient(app) as client:
        response = client.post("/predict", json={"features": SAMPLE + [1.0]})
        assert response.status_code == 422

def test_missing_body_and_unexpected_field():
    with TestClient(app) as client:
        assert client.post("/predict").status_code == 422
        response = client.post("/predict", json={"features": SAMPLE, "patient_name": "dato no permitido"})
        assert response.status_code == 422


def test_artifact_hash_and_positive_class():
    import hashlib
    from app.main import MODEL_PATH, META_PATH
    import json
    meta = json.loads(META_PATH.read_text())
    assert hashlib.sha256(MODEL_PATH.read_bytes()).hexdigest() == meta['training']['model_sha256']
    assert meta['target_mapping'] == {'0': 'maligno', '1': 'benigno'}
    assert meta['positive_class'] == 'benigno (1)'


def test_deployed_metrics_match_documented_split():
    import json
    import joblib
    from sklearn.datasets import load_breast_cancer
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
    from app.main import MODEL_PATH, META_PATH
    meta = json.loads(META_PATH.read_text())
    dataset = load_breast_cancer(as_frame=True)
    _, X_test, _, y_test = train_test_split(dataset.data, dataset.target, test_size=0.20, stratify=dataset.target, random_state=42)
    model = joblib.load(MODEL_PATH)
    pred = model.predict(X_test)
    actual = {'accuracy': accuracy_score(y_test,pred), 'precision':precision_score(y_test,pred), 'recall':recall_score(y_test,pred), 'f1':f1_score(y_test,pred), 'roc_auc':roc_auc_score(y_test,model.predict_proba(X_test)[:,1])}
    for name, value in actual.items():
        assert abs(value-meta['metrics'][name]) < 1e-12
    assert confusion_matrix(y_test,pred,labels=[0,1]).tolist() == meta['confusion_matrix']
