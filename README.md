# Fase II Clasificador de tumores con Docker y FastAPI

Prototipo académico que reutiliza el entrenamiento de la actividad 5 sobre Breast Cancer Wisconsin Diagnostic (569 registros y 30 características). Integra una interfaz web, una API de inferencia y un modelo versionado. No constituye diagnóstico médico.

## Arquitectura

Usuario → Nginx (8080) → proxy `/api` → FastAPI (8000) → pipeline de imputación, escalado y clasificación.

- `backend/app/main.py`: endpoints `/health`, `/model-info` y `/predict`.
- `backend/model/`: modelo desplegado y metadatos de su ejecución.
- `backend/tests/`: pruebas funcionales, contrato y coherencia del artefacto.
- `frontend/`: formulario, cliente JavaScript y proxy Nginx.
- `entrenamiento/`: datos, scripts, requisitos y resultados de Grid Search.
- `notebooks/entrena_cancer_colab.ipynb`: cuaderno para ejecutar el entrenamiento.
- `docs/`: manuales, pruebas, interpretación y vínculo con el chatbot.
- `.github/workflows/ci.yml`: pruebas, construcción y comprobación de integración.

## Ejecución local

Requiere Git, Docker Engine y Docker Compose v2.

```bash
git clone https://github.com/HamDan314/cancermm.git
cd cancermm
docker compose build
docker compose up -d
docker compose ps
curl --fail http://localhost:8080/api/health
docker compose exec -T backend python -m pytest -q
```

Frontend: http://localhost:8080. Swagger: http://localhost:8000/docs. Para detener: `docker compose down`.

## Reproducir el entrenamiento

```bash
python -m venv .venv
# Activar .venv según el sistema operativo
python -m pip install -r entrenamiento/requirements.txt
python entrenamiento/fuentes/train.py
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```

El script divide los datos 80/20 con estratificación y semilla 42. Ajusta los hiperparámetros con cinco pliegues de entrenamiento y selecciona el algoritmo por F1 promedio de validación cruzada. La decisión queda fijada antes de evaluar prueba. Las métricas de prueba de ambos modelos son descriptivas y no cambian la selección. No se ajusta el umbral: se conserva la regla `predict()` y su umbral predeterminado de 0.50.

La prueba histórica ya fue consultada en versiones anteriores: esta corrección mejora el procedimiento reproducible, pero no convierte la muestra existente en una evaluación externa inédita. Una confirmación adicional requiere datos independientes.

El script exporta el ganador a `backend/model/modelo_cancer.joblib` y genera `metadata.json` con métricas de esa misma instancia, versión, semilla, parámetros, versiones de paquetes, identificador MLflow y hashes del dataset, código y modelo. Reconstruir las imágenes después de reentrenar.

## Interpretación de resultados

La codificación es **0 maligno y 1 benigno**. Precision, recall y F1 se calculan para benigno. Un falso positivo de benignidad corresponde a un tumor maligno clasificado como benigno; un falso negativo de benignidad corresponde a un benigno clasificado como maligno. Las métricas deben leerse junto con la matriz y las consecuencias de cada error. Véase [validación e interpretación](docs/VALIDACION_Y_PRUEBAS.md).

## Documentación y evidencias

- [Manual de despliegue](docs/MANUAL_DESPLIEGUE_NUBE.md).
- [Validación y pruebas](docs/VALIDACION_Y_PRUEBAS.md).
- [Evidencia y comandos de Docker](docs/EVIDENCIA_CONTENEDOR.md).
- [Trazabilidad y resultados vigentes](docs/TRAZABILIDAD.md).
- [Relación con el chatbot generativo](docs/RELACION_CHATBOT.md).
- [Uso de herramientas de documentación](docs/USO_COPILOT_Y_DOCUMENTACION.md).

Los Word y PDF de la raíz conservan la entrega histórica. Para la revisión actual prevalecen los archivos Markdown y metadatos versionados; esos documentos históricos no se han reeditado.

Las pruebas de API no demuestran validez clínica. La construcción de una imagen tampoco demuestra una ejecución local o un despliegue en nube: conservar las salidas reales del entorno utilizado. No se ha implementado aquí el chatbot generativo.
