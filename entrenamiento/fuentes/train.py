"""Entrenamiento, ajuste y registro de modelos de clasificación con MLflow."""

from __future__ import annotations

import argparse
import hashlib
import platform
import subprocess
from datetime import datetime, timezone
from importlib.metadata import version
import json
import time
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.models import infer_signature
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    confusion_matrix,
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

from datos_prep import preparar_archivo, separar_xy, dividir_datos


RANDOM_STATE = 42


def construir_modelos(columnas):
    """Define pipelines y espacios de hiperparámetros."""
    preprocesador = ColumnTransformer(
        transformers=[("numericas", Pipeline([("imputacion", SimpleImputer(strategy="median")), ("escala", StandardScaler())]), list(columnas))],
        remainder="drop",
    )

    regresion = Pipeline(
        steps=[
            ("preprocesamiento", preprocesador),
            (
                "modelo",
                LogisticRegression(
                    max_iter=5000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )

    bosque = Pipeline(
        steps=[
            ("preprocesamiento", preprocesador),
            (
                "modelo",
                RandomForestClassifier(
                    random_state=RANDOM_STATE,
                    n_jobs=1,
                ),
            ),
        ]
    )

    return {
        "regresion_logistica": {
            "pipeline": regresion,
            "param_grid": {
                "modelo__C": [0.1, 1.0],
                "modelo__solver": ["liblinear"],
                "modelo__class_weight": [None, "balanced"],
            },
        },
        "random_forest": {
            "pipeline": bosque,
            "param_grid": {
                "modelo__n_estimators": [20, 50],
                "modelo__max_depth": [None, 10],
                "modelo__min_samples_split": [2, 5],
                "modelo__class_weight": [None, "balanced"],
            },
        },
    }


def calcular_metricas(y_true, y_pred, y_prob):
    """Calcula métricas estandarizadas para clasificación binaria."""
    return {
        "accuracy_test": accuracy_score(y_true, y_pred),
        "precision_test": precision_score(y_true, y_pred, zero_division=0),
        "recall_test": recall_score(y_true, y_pred, zero_division=0),
        "f1_test": f1_score(y_true, y_pred, zero_division=0),
        "roc_auc_test": roc_auc_score(y_true, y_prob),
    }


def guardar_matriz_confusion(modelo, X_test, y_test, destino):
    """Guarda la matriz de confusión como artefacto PNG."""
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_estimator(
        modelo,
        X_test,
        y_test,
        display_labels=["maligno", "benigno"],
        cmap="Blues",
        ax=ax,
    )
    ax.set_title("Matriz de confusión")
    fig.tight_layout()
    fig.savefig(destino, dpi=150)
    plt.close(fig)


def entrenar_y_registrar(
    nombre,
    configuracion,
    X_train,
    y_train,
    cv,
    carpeta_resultados,
):
    """Ejecuta GridSearchCV y registra parámetros, métricas y modelo."""
    scoring = {
        "accuracy": "accuracy",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
        "roc_auc": "roc_auc",
    }

    busqueda = GridSearchCV(
        estimator=configuracion["pipeline"],
        param_grid=configuracion["param_grid"],
        scoring=scoring,
        refit="f1",
        cv=cv,
        n_jobs=1,
        return_train_score=True,
        verbose=1,
    )

    inicio = time.perf_counter()
    busqueda.fit(X_train, y_train)
    duracion = time.perf_counter() - inicio

    mejor_modelo = busqueda.best_estimator_
    metricas = {}
    metricas["tiempo_entrenamiento_seg"] = duracion
    metricas["mejor_f1_cv"] = busqueda.best_score_
    metricas["f1_cv_desv"] = float(busqueda.cv_results_["std_test_f1"][busqueda.best_index_])

    carpeta_modelo = carpeta_resultados / nombre
    carpeta_modelo.mkdir(parents=True, exist_ok=True)

    resultados_cv = pd.DataFrame(busqueda.cv_results_)
    ruta_cv = carpeta_modelo / "resultados_gridsearch.csv"
    resultados_cv.to_csv(ruta_cv, index=False)


    ruta_modelo = carpeta_modelo / "modelo.joblib"
    joblib.dump(mejor_modelo, ruta_modelo)

    with mlflow.start_run(run_name=nombre):
        mlflow.set_tags(
            {
                "tipo_problema": "clasificacion_binaria",
                "dataset": "Breast Cancer Wisconsin Diagnostic",
                "algoritmo": nombre,
                "metodo_ajuste": "GridSearchCV",
                "cv": "StratifiedKFold_5",
            }
        )
        mlflow.log_params(busqueda.best_params_)
        mlflow.log_param("criterio_refit", "f1")
        mlflow.log_param("numero_folds", cv.get_n_splits())
        mlflow.log_metrics(metricas)
        mlflow.log_artifact(str(ruta_cv), artifact_path="validacion_cruzada")
        mlflow.log_artifact(str(ruta_modelo), artifact_path="modelo_joblib")

        firma = infer_signature(X_train, mejor_modelo.predict(X_train))
        mlflow.sklearn.log_model(
            sk_model=mejor_modelo,
            name="modelo",
            signature=firma,
            input_example=X_train.head(3),
        )

    fila = {
        "modelo": nombre,
        **busqueda.best_params_,
        **metricas,
    }
    return fila, mejor_modelo


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--entrada",
        default="datos/datos_ini/cancer_mama_original.csv",
        help="Ruta del CSV original.",
    )
    parser.add_argument(
        "--limpio",
        default="datos/datos_limp/cancer_mama_limpio.csv",
        help="Ruta del CSV limpio.",
    )
    parser.add_argument(
        "--tracking-uri",
        default="sqlite:///mlflow.db",
        help="URI de MLflow. Ejemplo: sqlite:///mlflow.db",
    )
    parser.add_argument(
        "--experimento",
        default="Actividad5_Clasificacion",
        help="Nombre del experimento en MLflow.",
    )
    args = parser.parse_args()

    raiz = Path(__file__).resolve().parents[1]
    entrada = raiz / args.entrada
    limpio = raiz / args.limpio
    resultados = raiz / "resultados"
    resultados.mkdir(exist_ok=True)

    df = preparar_archivo(entrada, limpio)
    X, y = separar_xy(df)
    X_train, X_test, y_train, y_test = dividir_datos(X, y)

    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(args.experimento)

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    resumen = []
    modelos = {}
    for nombre, configuracion in construir_modelos(X.columns).items():
        fila, modelo = entrenar_y_registrar(
            nombre,
            configuracion,
            X_train,
            y_train,
            cv,
            resultados,
        )
        resumen.append(fila)
        modelos[nombre] = modelo

    # La decisión se fija antes de consultar las etiquetas de prueba.
    resumen_df = pd.DataFrame(resumen).sort_values(
        by=["mejor_f1_cv", "modelo"], ascending=[False, True], kind="stable"
    )
    ganador = resumen_df.iloc[0]["modelo"]
    modelo = modelos[ganador]
    evaluaciones = {}
    for nombre, candidato in modelos.items():
        metricas = calcular_metricas(y_test, candidato.predict(X_test), candidato.predict_proba(X_test)[:, 1])
        evaluaciones[nombre] = metricas
        for clave, valor in metricas.items():
            resumen_df.loc[resumen_df["modelo"] == nombre, clave] = valor
        guardar_matriz_confusion(candidato, X_test, y_test, resultados / nombre / "matriz_confusion.png")
    # La comparación de prueba es descriptiva y no modifica al ganador.
    resumen_df.to_csv(resultados / "comparacion_modelos.csv", index=False)
    mejor = resumen_df.iloc[0].where(pd.notna(resumen_df.iloc[0]), None).to_dict()
    mejor["criterio_seleccion"] = "mayor F1 promedio en validación cruzada de entrenamiento; positivo=benigno"
    destino = raiz.parent / "backend" / "model"
    destino.mkdir(parents=True, exist_ok=True)
    ruta_desplegada = destino / "modelo_cancer.joblib"
    joblib.dump(modelo, ruta_desplegada)
    metrics = {k.removesuffix("_test"): v for k, v in evaluaciones[ganador].items()}
    metrics["test_samples"] = len(y_test)
    matriz = confusion_matrix(y_test, modelo.predict(X_test), labels=[0, 1]).tolist()
    try:
        revision = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=raiz, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        revision = "unknown"
    metadata = {
        "model_name": ganador, "version": "1.2.0", "target_mapping": {"0": "maligno", "1": "benigno"},
        "positive_class": "benigno (1)", "feature_names": list(X.columns), "metrics": metrics,
        "confusion_matrix_labels": ["maligno (0)", "benigno (1)"], "confusion_matrix": matriz,
        "decision_rule": "predict; umbral predeterminado 0.50 para clase 1; sin ajuste de umbral",
        "selection": {"criterion": "mean_test_f1", "folds": 5, "mean": mejor["mejor_f1_cv"], "std": mejor["f1_cv_desv"]},
        "training": {"random_state": RANDOM_STATE, "train_samples": len(y_train), "test_samples": len(y_test),
            "created_at_utc": datetime.now(timezone.utc).isoformat(), "git_parent_commit": revision,
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "dataset_sha256": hashlib.sha256(entrada.read_bytes()).hexdigest(),
            "model_sha256": hashlib.sha256(ruta_desplegada.read_bytes()).hexdigest(),
            "best_params": {k: v for k, v in modelo.get_params().items() if k in construir_modelos(X.columns)[ganador]["param_grid"]},
            "python": platform.python_version(), "packages": {n: version(n) for n in ["scikit-learn", "pandas", "joblib", "mlflow"]}}
    }
    for archivo, contenido in [(resultados / "mejor_modelo.json", mejor), (destino / "metadata.json", metadata)]:
        archivo.write_text(json.dumps(contenido, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
    with mlflow.start_run(run_name="seleccion_y_evaluacion_final") as run:
        mlflow.log_param("ganador_cv", ganador)
        mlflow.log_param("random_state", RANDOM_STATE)
        mlflow.log_param("decision_rule", metadata["decision_rule"])
        mlflow.log_metrics(evaluaciones[ganador])
        metadata["training"]["mlflow_run_id"] = run.info.run_id
        (destino / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False, allow_nan=False), encoding="utf-8")
        mlflow.log_artifacts(str(destino), artifact_path="modelo_desplegado")
        mlflow.log_artifact(str(resultados / "comparacion_modelos.csv"))

    print("\nComparación final:")
    print(resumen_df.to_string(index=False))
    print("\nPara abrir MLflow:")
    print("mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000")


if __name__ == "__main__":
    main()
